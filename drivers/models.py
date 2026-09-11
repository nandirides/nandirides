from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Driver(TimeStampedModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"
        BLOCKED = "blocked", "Blocked"

    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver",
    )

    driver_code = models.CharField(
        max_length=50,
        unique=True,
    )

    license_number = models.CharField(
        max_length=100,
        unique=True,
    )

    license_expiry = models.DateField(
        null=True,
        blank=True,
    )

    experience_years = models.PositiveIntegerField(
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )

    total_rides = models.PositiveIntegerField(
        default=0,
    )

    def __str__(self):
        return self.driver_code

class DriverDocument(TimeStampedModel):

    class DocumentType(models.TextChoices):
        LICENSE = "license", "Driving License"
        AADHAAR = "aadhaar", "Aadhaar"
        PAN = "pan", "PAN"
        ADDRESS_PROOF = "address_proof", "Address Proof"
        POLICE = "police", "Police Verification"
        MEDICAL = "medical", "Medical Certificate"

    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    driver = models.ForeignKey(
        Driver,
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
        upload_to="driver_documents/",
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
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_driver_documents",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

class DriverBankAccount(TimeStampedModel):

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
    )

    account_holder_name = models.CharField(
        max_length=150,
    )

    account_number = models.CharField(
        max_length=50,
    )

    ifsc_code = models.CharField(
        max_length=20,
    )

    bank_name = models.CharField(
        max_length=150,
    )

    upi_id = models.CharField(
        max_length=100,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    verification_status = models.CharField(
        max_length=20,
        default="pending",
    )


class DriverEarning(TimeStampedModel):

    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name="earnings",
    )

    ride = models.OneToOneField(
        "rides.Ride",
        on_delete=models.PROTECT,
        related_name="driver_earning",
    )

    gross_fare = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    penalty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    net_earning = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        default="pending",
    )


class DriverPayout(TimeStampedModel):

    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name="payouts",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payout_reference = models.CharField(
        max_length=255,
        blank=True,
    )

    payment_method = models.CharField(
        max_length=30,
        default="bank_transfer",
    )

    status = models.CharField(
        max_length=20,
        default="pending",
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )



