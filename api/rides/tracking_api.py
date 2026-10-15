
import hashlib
import json
import secrets
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rides.models import Ride, RideRequest, RideTracking

def _ride_status_label(ride_status):
    labels = {
        "driver_assigned": "Driver assigned",
        "driver_arriving": "Driver arriving",
        "driver_arrived": "Driver arrived",
        "started": "Ride in progress",
        "completed": "Ride completed",
        "cancelled": "Ride cancelled",
    }
    return labels.get(ride_status, str(ride_status).replace("_", " ").title())

def _error(message, code):
    return Response({"success": False, "detail": message}, status=code)

def _otp_cache_key(ride_id):
    return f"nandiride:pickup-otp:{ride_id}"

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ride_request_tracking(request, request_id):
    try:
        ride_request = RideRequest.objects.select_related(
            "pickup_location", "drop_location", "vehicle_type"
        ).get(pk=request_id, passenger=request.user)
    except RideRequest.DoesNotExist:
        return _error("Booking not found.", status.HTTP_404_NOT_FOUND)

    ride = (
        Ride.objects.filter(ride_request=ride_request)
        .select_related("driver__user", "vehicle", "pickup_location", "drop_location")
        .first()
    )
    current_status = ride.status if ride else ride_request.status
    result = {
        "request_id": ride_request.pk,
        "request_number": ride_request.request_number,
        "request_status": ride_request.status,
        "status": current_status,
        "status_label": _ride_status_label(current_status),
        "pickup": str(ride_request.pickup_location),
        "drop": str(ride_request.drop_location),
        "fare": str(
            ride_request.final_fare
            if ride_request.final_fare is not None
            else ride_request.estimated_fare or Decimal("0")
        ),
        "ride_id": ride.pk if ride else None,
        "driver": None,
        "vehicle": None,
        "location": None,
        "pickup_otp": None,
    }
    if ride:
        result["driver"] = {
            "name": ride.driver.user.get_full_name() or ride.driver.user.get_username(),
            "phone": getattr(ride.driver, "phone", ""),
            "rating": str(getattr(ride.driver, "rating", "")),
        }
        result["vehicle"] = {
            "number": getattr(ride.vehicle, "registration_number", ""),
            "name": str(ride.vehicle),
        }
        latest = ride.tracking_points.order_by("-recorded_at").first()
        if latest:
            result["location"] = {
                "latitude": float(latest.latitude),
                "longitude": float(latest.longitude),
                "recorded_at": latest.recorded_at.isoformat(),
            }
        if (
            ride.status == Ride.Status.DRIVER_ARRIVED
            and ride.pickup_otp_hash
            and ride.pickup_otp_expires_at
            and ride.pickup_otp_expires_at > timezone.now()
            and not ride.pickup_otp_verified_at
        ):
            result["pickup_otp"] = cache.get(_otp_cache_key(ride.pk))
    return Response(result)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def driver_update_ride_location(request, ride_id):
    try:
        driver = request.user.driver
    except Exception:
        return _error("Driver account required.", status.HTTP_403_FORBIDDEN)
    try:
        latitude = Decimal(str(request.data["latitude"]))
        longitude = Decimal(str(request.data["longitude"]))
    except (KeyError, InvalidOperation, TypeError, ValueError):
        return _error("Valid latitude and longitude are required.", status.HTTP_400_BAD_REQUEST)
    if not Decimal("-90") <= latitude <= Decimal("90"):
        return _error("Latitude is out of range.", status.HTTP_400_BAD_REQUEST)
    if not Decimal("-180") <= longitude <= Decimal("180"):
        return _error("Longitude is out of range.", status.HTTP_400_BAD_REQUEST)
    try:
        ride = Ride.objects.get(pk=ride_id, driver=driver)
    except Ride.DoesNotExist:
        return _error("Ride not found for this driver.", status.HTTP_404_NOT_FOUND)
    if ride.status not in {
        Ride.Status.DRIVER_ASSIGNED,
        Ride.Status.DRIVER_ARRIVING,
        Ride.Status.DRIVER_ARRIVED,
        Ride.Status.STARTED,
    }:
        return _error("Location updates are not allowed for this ride status.", status.HTTP_400_BAD_REQUEST)
    tracking = RideTracking.objects.create(
        ride=ride,
        driver=driver,
        latitude=latitude,
        longitude=longitude,
    )
    return Response(
        {"success": True, "recorded_at": tracking.recorded_at.isoformat()},
        status=status.HTTP_201_CREATED,
    )

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def driver_update_ride_status(request, ride_id):
    try:
        driver = request.user.driver
    except Exception:
        return _error("Driver account required.", status.HTTP_403_FORBIDDEN)
    action_name = str(request.data.get("action", "")).strip().lower()
    with transaction.atomic():
        try:
            ride = Ride.objects.select_for_update().get(pk=ride_id, driver=driver)
        except Ride.DoesNotExist:
            return _error("Ride not found for this driver.", status.HTTP_404_NOT_FOUND)
        if action_name == "arriving":
            if ride.status != Ride.Status.DRIVER_ASSIGNED:
                return _error("Ride cannot be marked arriving from its current status.", status.HTTP_400_BAD_REQUEST)
            ride.status = Ride.Status.DRIVER_ARRIVING
            ride.save(update_fields=["status"])
        elif action_name == "arrived":
            if ride.status not in {Ride.Status.DRIVER_ASSIGNED, Ride.Status.DRIVER_ARRIVING}:
                return _error("Ride cannot be marked arrived from its current status.", status.HTTP_400_BAD_REQUEST)
            otp = f"{secrets.randbelow(1_000_000):06d}"
            ride.pickup_otp_hash = hashlib.sha256(otp.encode()).hexdigest()
            ride.pickup_otp_expires_at = timezone.now() + timedelta(minutes=10)
            ride.pickup_otp_verified_at = None
            ride.status = Ride.Status.DRIVER_ARRIVED
            ride.arrived_at = timezone.now()
            ride.save(update_fields=[
                "pickup_otp_hash", "pickup_otp_expires_at",
                "pickup_otp_verified_at", "status", "arrived_at",
            ])
            cache.set(_otp_cache_key(ride.pk), otp, timeout=600)
        elif action_name == "start":
            supplied_otp = str(request.data.get("otp", "")).strip()
            if ride.status != Ride.Status.DRIVER_ARRIVED:
                return _error("Driver must arrive before starting the ride.", status.HTTP_400_BAD_REQUEST)
            if not supplied_otp.isdigit() or len(supplied_otp) != 6:
                return _error("Enter the six-digit pickup OTP.", status.HTTP_400_BAD_REQUEST)
            if not ride.pickup_otp_expires_at or ride.pickup_otp_expires_at <= timezone.now():
                return _error("Pickup OTP has expired.", status.HTTP_400_BAD_REQUEST)
            supplied_hash = hashlib.sha256(supplied_otp.encode()).hexdigest()
            if not secrets.compare_digest(supplied_hash, ride.pickup_otp_hash):
                return _error("Incorrect pickup OTP.", status.HTTP_400_BAD_REQUEST)
            ride.pickup_otp_verified_at = timezone.now()
            ride.status = Ride.Status.STARTED
            ride.started_at = timezone.now()
            ride.save(update_fields=["pickup_otp_verified_at", "status", "started_at"])
            cache.delete(_otp_cache_key(ride.pk))
        elif action_name == "complete":
            if ride.status != Ride.Status.STARTED:
                return _error("Only an active trip can be completed.", status.HTTP_400_BAD_REQUEST)
            ride.status = Ride.Status.COMPLETED
            ride.completed_at = timezone.now()
            ride.save(update_fields=["status", "completed_at"])
        else:
            return _error("Unsupported action.", status.HTTP_400_BAD_REQUEST)
    return Response({
        "success": True,
        "ride_id": ride.pk,
        "status": ride.status,
        "status_label": _ride_status_label(ride.status),
    })
