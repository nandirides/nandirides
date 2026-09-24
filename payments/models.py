from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Payment(TimeStampedModel):

    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        UPI = "upi", "UPI"
        CARD = "card", "Card"
        WALLET = "wallet", "Wallet"
        NETBANKING = "netbanking", "Net Banking"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    payment_number = models.CharField(
        max_length=50,
        unique=True,
    )

    ride = models.OneToOneField(
        "rides.Ride",
        on_delete=models.PROTECT,
        related_name="payment",
        null=True,
        blank=True,
    )

    ride_request = models.OneToOneField(
        "rides.RideRequest",
        on_delete=models.PROTECT,
        related_name="payment",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=Method.choices,
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
    )

    gateway = models.CharField(
        max_length=100,
        blank=True,
    )

    gateway_order_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
    )

    card_brand = models.CharField(
        max_length=30,
        blank=True,
    )

    card_last4 = models.CharField(
        max_length=4,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )


class Refund(TimeStampedModel):

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )

    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    reason = models.TextField(
        blank=True,
    )

    refund_reference = models.CharField(
        max_length=255,
        blank=True,
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