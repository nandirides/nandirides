from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from drivers.models import Driver
from locations.models import Location
from vehicles.models import Vehicle, VehicleType


class RideRequest(TimeStampedModel):

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        SEARCHING = "searching_driver", "Searching Driver"
        ASSIGNED = "driver_assigned", "Driver Assigned"
        ACCEPTED = "accepted", "Accepted"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"
        COMPLETED = "completed", "Completed"

    request_number = models.CharField(
        max_length=50,
        unique=True,
    )

    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ride_requests",
    )

    pickup_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="pickup_requests",
    )

    drop_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="drop_requests",
    )

    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    estimated_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    estimated_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    estimated_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
    )

class Ride(TimeStampedModel):

    class Status(models.TextChoices):
        DRIVER_ASSIGNED = "driver_assigned", "Driver Assigned"
        DRIVER_ARRIVING = "driver_arriving", "Driver Arriving"
        DRIVER_ARRIVED = "driver_arrived", "Driver Arrived"
        STARTED = "started", "Started"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    ride_number = models.CharField(
        max_length=50,
        unique=True,
    )

    ride_request = models.OneToOneField(
        RideRequest,
        on_delete=models.PROTECT,
        related_name="ride",
    )

    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rides_as_passenger",
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name="rides",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="rides",
    )

    pickup_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="ride_pickups",
    )

    drop_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="ride_drops",
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    arrived_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    duration_minutes = models.PositiveIntegerField(
        default=0,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRIVER_ASSIGNED,
        db_index=True,
    )

    def __str__(self):
        return self.ride_number



class RideStop(TimeStampedModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ARRIVED = "arrived", "Arrived"
        COMPLETED = "completed", "Completed"

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="stops",
    )

    stop_order = models.PositiveIntegerField()

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
    )

    arrival_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    departure_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        ordering = ["stop_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["ride", "stop_order"],
                name="unique_ride_stop_order",
            )
        ]

class RideDriverAssignment(TimeStampedModel):

    class Status(models.TextChoices):
        ASSIGNED = "assigned", "Assigned"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="driver_assignments",
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name="ride_assignments",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejection_reason = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED,
    )

class RideTracking(models.Model):

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="tracking_points",
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    speed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    heading = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    accuracy = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["ride", "-recorded_at"]
            )
        ]

class CancellationReason(TimeStampedModel):

    class Type(models.TextChoices):
        PASSENGER = "passenger", "Passenger"
        DRIVER = "driver", "Driver"
        SYSTEM = "system", "System"
        ADMIN = "admin", "Admin"

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )

    reason = models.CharField(
        max_length=255,
    )

    charge_applicable = models.BooleanField(
        default=False,
    )

    charge_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )


class RideCancellation(TimeStampedModel):

    ride = models.OneToOneField(
        Ride,
        on_delete=models.PROTECT,
        related_name="cancellation",
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    reason = models.ForeignKey(
        CancellationReason,
        on_delete=models.PROTECT,
    )

    reason_text = models.TextField(
        blank=True,
    )

    cancellation_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    cancelled_at = models.DateTimeField(
        auto_now_add=True,
    )


class RideRating(TimeStampedModel):

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="ratings",
    )

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ratings_given",
    )

    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ratings_received",
    )

    rating = models.PositiveSmallIntegerField()

    review = models.TextField(
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "ride",
                    "from_user",
                    "to_user",
                ],
                name="unique_ride_rating",
            )
        ]

    def __str__(self):
        return f"{self.rating}/5"

