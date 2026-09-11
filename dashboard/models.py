from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

# class User(models.Model):
#     usernamename = models.CharField(max_length=100)
#     email = models.EmailField()
#     # roll = models.IntegerField()

    # def __str__(self):
    #     return self.name
        
class Gallery(models.Model):
    profile_image = models.ImageField(upload_to='profileimg', blank=True,
                                      help_text='Optional: Upload a profile image')
    my_file = models.FileField(upload_to = 'doc', blank=True)
    date = models.DateTimeField(auto_now_add = True)

    def delete(self, *args, **kwargs):
        if self.profile_image:
            self.profile_image.delete(save=False)

        super().delete(*args, **kwargs)


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