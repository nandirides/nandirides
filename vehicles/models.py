from django.db import models

from core.models import TimeStampedModel
from drivers.models import Driver


class VehicleType(TimeStampedModel):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.CharField(
        max_length=30,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    capacity = models.PositiveIntegerField(
        default=4,
    )

    base_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    per_km_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    per_minute_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name

class Vehicle(TimeStampedModel):

    class FuelType(models.TextChoices):
        PETROL = "petrol", "Petrol"
        DIESEL = "diesel", "Diesel"
        CNG = "cng", "CNG"
        ELECTRIC = "electric", "Electric"
        HYBRID = "hybrid", "Hybrid"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        MAINTENANCE = "maintenance", "Maintenance"
        BLOCKED = "blocked", "Blocked"

    vehicle_number = models.CharField(
        max_length=30,
        unique=True,
    )

    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        related_name="vehicles",
    )

    brand = models.CharField(
        max_length=100,
    )

    model = models.CharField(
        max_length=100,
    )

    variant = models.CharField(
        max_length=100,
        blank=True,
    )

    manufacturing_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    color = models.CharField(
        max_length=50,
        blank=True,
    )

    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
    )

    seating_capacity = models.PositiveIntegerField(
        default=4,
    )

    registration_date = models.DateField(
        null=True,
        blank=True,
    )

    registration_expiry = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    def __str__(self):
        return self.vehicle_number

class DriverVehicle(TimeStampedModel):

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="vehicle_assignments",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="driver_assignments",
    )

    assigned_from = models.DateTimeField()

    assigned_to = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_current = models.BooleanField(
        default=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["driver", "is_current"]
            ),
            models.Index(
                fields=["vehicle", "is_current"]
            ),
        ]

class VehicleDocument(TimeStampedModel):

    class DocumentType(models.TextChoices):
        RC = "rc", "Registration Certificate"
        INSURANCE = "insurance", "Insurance"
        PUC = "puc", "PUC"
        PERMIT = "permit", "Permit"
        FITNESS = "fitness", "Fitness Certificate"

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
    )

    document_file = models.FileField(
        upload_to="vehicle_documents/",
    )

    issue_date = models.DateField(
        null=True,
        blank=True,
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    verification_status = models.CharField(
        max_length=20,
        default="pending",
    )


