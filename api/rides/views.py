from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rides.models import Ride, RideRequest
from .serializers import RideRequestSerializer, RideSerializer, FareEstimationSerializer
from .services import calculate_fare
from rest_framework.views import APIView

class FareEstimationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FareEstimationSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        result = calculate_fare(
            pickup=data["pickup_location"],
            drop=data["drop_location"],
            vehicle_type=data["vehicle_type"],
            user=request.user,
            coupon_code=data.get("coupon_code", "")
        )

        return Response(
            result,
            status=status.HTTP_200_OK
        )

class RideRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RideRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            RideRequest.objects
            .select_related(
                "passenger",
                "pickup_location",
                "drop_location",
                "vehicle_type",
            )
            .filter(
                passenger=self.request.user
            )
            .order_by(
                "-requested_at"
            )
        )

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        return Response(
            {
                "success": False,
                "message": "Ride request cannot be updated."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {
                "success": False,
                "message": "Ride request cannot be updated."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "success": False,
                "message": "Ride request cannot be deleted."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="cancel"
    )
    def cancel(self, request, pk=None):
        ride_request = self.get_object()

        if ride_request.status not in [
            RideRequest.Status.REQUESTED,
            RideRequest.Status.SEARCHING,
        ]:
            return Response(
                {
                    "success": False,
                    "message": "This ride request cannot be cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        ride_request.status = RideRequest.Status.CANCELLED
        ride_request.save(
            update_fields=["status"]
        )

        return Response(
            {
                "success": True,
                "message": "Ride request cancelled successfully.",
                "data": RideRequestSerializer(
                    ride_request,
                    context={
                        "request": request
                    }
                ).data
            },
            status=status.HTTP_200_OK
        )


class RideViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Ride.objects
            .select_related(
                "passenger",
                "driver",
                "driver__user",
                "vehicle",
                "vehicle__vehicle_type",
                "ride_request",
                "pickup_location",
                "drop_location",
            )
            .filter(
                passenger=self.request.user
            )
            .order_by(
                "-created_at"
            )
        )