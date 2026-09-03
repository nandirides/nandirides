from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Booking(models.Model):
    booking_id = models.CharField(max_length=200, unique=True)
    pickup_location = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    ride_type = models.CharField(max_length=200)
    ride_date = models.CharField(max_length=200)
    ride_time = models.CharField(max_length=200)
    ride_status = models.CharField(max_length=200)
    passengers = models.CharField(max_length=200)
    note = models.CharField(max_length=200)
    base_fare = models.CharField(max_length=200)
    ride_charge = models.CharField(max_length=200)
    distance = models.CharField(max_length=200)
    platform_fee = models.CharField(max_length=200)
    total_amount = models.CharField(max_length=200)
    completed_ride = models.CharField(max_length=200)
    total_ride = models.CharField(max_length=200)
    total_spent = models.CharField(max_length=200)
    fare = models.CharField(max_length=200)
    estimate_fare = models.CharField(max_length=200)
    your_rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)

class Driver(models.Model):
    driver_id = models.CharField(max_length=200)
    driver_name = models.CharField(max_length=200)
    driver_phone = models.CharField(max_length=200)
    driver_email = models.CharField(max_length=200)
    driver_registration = models.CharField(max_length=200)
    driver_status = models.CharField(max_length=200)
    driver_arrival = models.CharField(max_length=200)
    dl_number = models.CharField(max_length=200)
    vehicle_number = models.CharField(max_length=200)
    vehicle_insurance = models.CharField(max_length=200)
    vehicle_pollution = models.CharField(max_length=200)
    vehicle_type = models.CharField(max_length=200)
    documnet_upload = models.FileField(upload_to='profile/', blank=True, null=True)

class MyRide(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='my_ride')
    ride_id = models.CharField(max_length=200)
    ride_date = models.CharField(max_length=200)
    ride_time = models.CharField(max_length=200)
    ride_type = models.CharField(max_length=200)
    ride_track = models.CharField(max_length=200)

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=200)
    payment_date = models.CharField(max_length=200)
    payment_time = models.CharField(max_length=200)
    payment_type = models.CharField(max_length=200)
    payment_receipt = models.CharField(max_length=200)
class User(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ("other", "Other"),
    ]

    COUNTRY_CHOICES = [
            ('INDIA', 'INDIA'),
            ('USA', 'USA'),
            ("CHINA", "CHINA"),
        ]

    STATE_CHOICES = [
            ('UP', 'Uttar Pradesh'),
            ('BR', 'Bihar'),
            ("CDG", "Chandigarh"),
        ]
    
    DISTRICT_CHOICES = [
            ('AGC', 'AGRA'),
            ('VNR', 'VARANASI'),
            ("MTJ", "MATHURA"),
        ]

    profileimage = models.ImageField(upload_to='profile/', blank=True, null=True)
    user_id = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    confirmpassword = models.CharField(max_length=200)
    oldpassword = models.CharField(max_length=200)
    newpassword = models.CharField(max_length=200)
    newconfirmpassword = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    dob = models.DateField()
    address = models.CharField(max_length=100)
    village_colony = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    pincode = models.CharField(max_length=200)
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)
    district = models.CharField(max_length=20, choices=DISTRICT_CHOICES)
    mobilenumber = models.CharField(max_length=200)
    usertype = models.CharField(max_length=200)
    regdate = models.CharField(max_length=200)
    dlnumber = models.CharField(max_length=200)
    vehiclenumber = models.CharField(max_length=200)
    vehicleinsurance = models.CharField(max_length=200)
    vehiclepollution = models.CharField(max_length=200)
    vehicletype = models.CharField(max_length=200)
    documnetupload = models.FileField(upload_to='profile/', blank=True, null=True)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

