
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drivers.models import Driver
from rides.models import Ride, RideRequest, RideDriverAssignment
from vehicles.models import DriverVehicle, Vehicle
from .serializers import RideSerializer

class DriverRideRequestSerializer(serializers.ModelSerializer):
    pickup_details = serializers.SerializerMethodField()
    drop_details = serializers.SerializerMethodField()
    vehicle_type_name = serializers.CharField(source="vehicle_type.name", read_only=True)
    estimated_distance_km = serializers.DecimalField(source="estimated_distance", max_digits=10, decimal_places=2, read_only=True, allow_null=True)
    estimated_duration_minutes = serializers.IntegerField(source="estimated_duration", read_only=True, allow_null=True)

    class Meta:
        model = RideRequest
        fields = [
            "id",
            "request_number",
            "pickup_details",
            "drop_details",
            "vehicle_type_name",
            "estimated_distance_km",
            "estimated_duration_minutes",
            "estimated_fare",
            "discount_amount",
            "final_fare",
            "status",
            "requested_at",
            "scheduled_at",
        ]

    def get_pickup_details(self, obj):
        location = obj.pickup_location
        return {
            "id": location.pk,
            "address": location.address,
            "city": str(location.city),
            "latitude": getattr(location, "latitude", None),
            "longitude": getattr(location, "longitude", None),
        }

    def get_drop_details(self, obj):
        location = obj.drop_location
        return {
            "id": location.pk,
            "address": location.address,
            "city": str(location.city),
            "latitude": getattr(location, "latitude", None),
            "longitude": getattr(location, "longitude", None),
        }


def get_driver_for_user(user):
    try:
        driver = Driver.objects.get(user=user)
    except Driver.DoesNotExist:
        return None, "Driver profile not found."
    if driver.status != Driver.Status.ACTIVE:
        return None, "Your driver account is not active."
    if driver.verification_status != Driver.VerificationStatus.VERIFIED:
        return None, "Your driver account is not verified."
    if not driver.is_online:
        return None, "Go online before accessing ride requests."
    return driver, None


class DriverRideRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver, error = get_driver_for_user(request.user)
        if error:
            return Response({"detail": error}, status=status.HTTP_403_FORBIDDEN)
        vehicle_type_ids = DriverVehicle.objects.filter(
            driver=driver,
            is_current=True,
            vehicle__status=Vehicle.Status.ACTIVE,
        ).values_list("vehicle__vehicle_type_id", flat=True)
        if not vehicle_type_ids.exists():
            return Response(
                {"detail": "No active vehicle is assigned to your profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        requests = (
            RideRequest.objects
            .filter(
                vehicle_type_id__in=vehicle_type_ids,
                status__in=[
                    RideRequest.Status.REQUESTED,
                    RideRequest.Status.SEARCHING,
                ],
                ride__isnull=True,
            )
            .select_related(
                "passenger",
                "pickup_location",
                "pickup_location__city",
                "drop_location",
                "drop_location__city",
                "vehicle_type",
            )
            .order_by("-requested_at")
            .distinct()
        )
        data = DriverRideRequestSerializer(requests, many=True).data
        return Response({
            "count": len(data),
            "results": data,
        })


class DriverAcceptRideAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        driver, error = get_driver_for_user(request.user)
        if error:
            return Response({"detail": error}, status=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            ride_request = get_object_or_404(
                RideRequest.objects.select_for_update(),
                pk=request_id,
            )
            if ride_request.status not in [
                RideRequest.Status.REQUESTED,
                RideRequest.Status.SEARCHING,
            ]:
                return Response(
                    {"detail": "This ride request is no longer available."},
                    status=status.HTTP_409_CONFLICT,
                )
            if Ride.objects.filter(ride_request=ride_request).exists():
                return Response(
                    {"detail": "This ride has already been assigned."},
                    status=status.HTTP_409_CONFLICT,
                )
            assignment = (
                DriverVehicle.objects
                .select_related("vehicle", "vehicle__vehicle_type")
                .filter(
                    driver=driver,
                    is_current=True,
                    vehicle__status=Vehicle.Status.ACTIVE,
                    vehicle__vehicle_type=ride_request.vehicle_type,
                )
                .order_by("-created_at")
                .first()
            )
            if assignment is None:
                return Response(
                    {"detail": "No active matching vehicle is assigned to you."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ride = Ride.objects.create(
                ride_request=ride_request,
                passenger=ride_request.passenger,
                driver=driver,
                vehicle=assignment.vehicle,
                pickup_location=ride_request.pickup_location,
                drop_location=ride_request.drop_location,
                scheduled_at=ride_request.scheduled_at,
                distance_km=ride_request.estimated_distance or 0,
                duration_minutes=ride_request.estimated_duration or 0,
                status=Ride.Status.DRIVER_ASSIGNED,
            )
            ride_request.status = RideRequest.Status.ACCEPTED
            ride_request.save(update_fields=["status", "updated_at"])
            RideDriverAssignment.objects.create(
                ride=ride,
                driver=driver,
                status=RideDriverAssignment.Status.ACCEPTED,
                accepted_at=timezone.now(),
            )
        return Response(
            {
                "success": True,
                "message": "Ride accepted successfully.",
                "ride": RideSerializer(
                    ride,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )

class DriverRideDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ride_id):
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return Response(
                {"detail": "Driver profile not found."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ride = (
                Ride.objects
                .select_related(
                    "ride_request",
                    "passenger",
                    "driver",
                    "driver__user",
                    "vehicle",
                    "vehicle__vehicle_type",
                    "pickup_location",
                    "drop_location",
                    "ride_request__vehicle_type",
                )
                .get(pk=ride_id, driver=driver)
            )
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Ride not found for this driver."},
                status=status.HTTP_404_NOT_FOUND,
            )

        ride_request = ride.ride_request

        return Response({
            "success": True,
            "ride": RideSerializer(
                ride,
                context={"request": request},
            ).data,
            "pickup_details": {
                "address": ride.pickup_location.address,
                "city": str(ride.pickup_location.city),
                "latitude": getattr(ride.pickup_location, "latitude", None),
                "longitude": getattr(ride.pickup_location, "longitude", None),
            },
            "drop_details": {
                "address": ride.drop_location.address,
                "city": str(ride.drop_location.city),
                "latitude": getattr(ride.drop_location, "latitude", None),
                "longitude": getattr(ride.drop_location, "longitude", None),
            },
            "fare": str(
                ride_request.final_fare
                if ride_request.final_fare is not None
                else ride_request.estimated_fare
                if ride_request.estimated_fare is not None
                else 0
            ),
            "discount_amount": str(ride_request.discount_amount or 0),
            "distance_km": str(ride.distance_km),
            "duration_minutes": ride.duration_minutes,
        })
