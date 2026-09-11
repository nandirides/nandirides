from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Coupon(TimeStampedModel):

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed Amount"

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    minimum_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    per_user_limit = models.PositiveIntegerField(
        default=1,
    )

    valid_from = models.DateTimeField()

    valid_to = models.DateTimeField()

    is_active = models.BooleanField(
        default=True,
    )


class CouponUsage(TimeStampedModel):

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.PROTECT,
        related_name="usages",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coupon_usages",
    )

    ride = models.ForeignKey(
        "rides.Ride",
        on_delete=models.PROTECT,
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    used_at = models.DateTimeField(
        auto_now_add=True,
    )