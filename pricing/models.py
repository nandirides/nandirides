from django.db import models

from core.models import TimeStampedModel
from locations.models import City
from vehicles.models import VehicleType


class FareRule(TimeStampedModel):

    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.CASCADE,
        related_name="fare_rules",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="fare_rules",
    )

    base_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    minimum_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    per_km_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    per_minute_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    waiting_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    cancellation_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    effective_from = models.DateTimeField()

    effective_to = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )


class FareBreakdown(TimeStampedModel):

    ride = models.OneToOneField(
        "rides.Ride",
        on_delete=models.CASCADE,
        related_name="fare",
    )

    base_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    distance_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    time_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    waiting_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    surge_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    toll_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    parking_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    tip = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

class SurgePricing(TimeStampedModel):

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
    )

    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.CASCADE,
    )

    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    reason = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )


