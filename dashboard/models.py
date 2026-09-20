from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

# class User(models.Model):
#     usernamename = models.CharField(max_length=100)
#     email = models.EmailField()
#     # roll = models.IntegerField()
#
#     def __str__(self):
#         return self.name

class Gallery(models.Model):
    class Category(models.TextChoices):
        PROFILE = "profile", "Profile"
        VEHICLE = "vehicle", "Vehicle"
        RIDE = "ride", "Ride"
        DRIVER = "driver", "Driver"
        OTHER = "other", "Other"

    profile_image = models.ImageField(
        upload_to="profileimg/",
        blank=False,
        null=False,
        help_text="Required: Upload a gallery image",
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    date = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.profile_image:
            self.profile_image.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.get_category_display()} - {self.profile_image.name}"


class UserProfile(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
    )
    address = models.TextField(
        blank=True,
    )
    city = models.ForeignKey(
        "locations.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
    )
    emergency_contact_name = models.CharField(
        max_length=150,
        blank=True,
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
    )
    email_verified = models.BooleanField(
        default=False,
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.get_username()

class UserAddress(TimeStampedModel):
    class AddressType(models.TextChoices):
        HOME = "home", "Home"
        OFFICE = "office", "Office"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.OTHER,
    )
    label = models.CharField(
        max_length=100,
        blank=True,
    )
    address_line1 = models.CharField(
        max_length=255,
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
    )
    landmark = models.CharField(
        max_length=255,
        blank=True,
    )
    city = models.ForeignKey(
        "locations.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    is_default = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.label or self.address_line1


class AccountNotificationPreference(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences"
    )
    platform_updates = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    ride_activity = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification Preferences - {self.user.get_username()}"


class AccountPaymentDetail(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_details",
    )
    upi_id = models.CharField(
        max_length=100,
        blank=True,
    )
    wallet_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    card_last_four = models.CharField(
        max_length=4,
        blank=True,
    )
    card_brand = models.CharField(
        max_length=30,
        blank=True,
    )
    card_expiry = models.CharField(
        max_length=7,
        blank=True,
    )

    def __str__(self):
        return f"Payment Details - {self.user.get_username()}"

class WalletTransaction(TimeStampedModel):
    class TransactionType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        PENDING = "pending", "Pending"
        FAILED = "failed", "Failed"
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet_transactions",
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        default=TransactionType.CREDIT,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.SUCCESS,
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
    )
    def __str__(self):
        return f"{self.user.get_username()} - {self.transaction_type} - ₹{self.amount}"