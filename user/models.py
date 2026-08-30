from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

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

