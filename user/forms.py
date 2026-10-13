from decimal import Decimal
import re
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from dashboard.models import UserProfile, UserAddress
from locations.models import City
from rides.models import RideRequest
from payments.models import Payment
from vehicles.models import VehicleType

AuthUser = get_user_model()

BOOTSTRAP_INPUT = "form-control"
BOOTSTRAP_SELECT = "form-select"
BOOTSTRAP_CHECKBOX = "form-check-input"

def add_bootstrap_class(field, css_class=BOOTSTRAP_INPUT):
    existing = field.widget.attrs.get("class", "")
    classes = existing.split()
    if css_class not in classes:
        classes.append(css_class)
    field.widget.attrs["class"] = " ".join(classes)

def add_placeholder(field, placeholder):
    if placeholder:
        field.widget.attrs.setdefault("placeholder", placeholder)

def style_form_fields(form):
    for name, field in form.fields.items():
        if isinstance(field.widget, forms.Select):
            add_bootstrap_class(field, BOOTSTRAP_SELECT)
        elif isinstance(field.widget, forms.CheckboxInput):
            add_bootstrap_class(field, BOOTSTRAP_CHECKBOX)
        elif not isinstance(field.widget, forms.HiddenInput):
            add_bootstrap_class(field, BOOTSTRAP_INPUT)

class CustomerCreateForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Email address", "autocomplete": "email"}),
    )
    first_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "First name", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Last name", "autocomplete": "family-name"}),
    )

    class Meta:
        model = AuthUser
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)
        placeholders = {
            "username": "Username",
            "password1": "Password",
            "password2": "Confirm password",
        }
        for name, placeholder in placeholders.items():
            if name in self.fields:
                add_placeholder(self.fields[name], placeholder)
        if "username" in self.fields:
            self.fields["username"].widget.attrs.setdefault("autocomplete", "username")
        if "password1" in self.fields:
            self.fields["password1"].widget.attrs.update({"autocomplete": "new-password"})
        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.update({"autocomplete": "new-password"})
        if self.instance and self.instance.pk and "username" in self.fields:
            self.fields["username"].disabled = True

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        queryset = AuthUser._default_manager.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("This email address is already registered.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ("user", "created_at", "updated_at")
        widgets = {
            "phone": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Phone number", "autocomplete": "tel"}),
            "date_of_birth": forms.DateInput(attrs={"class": BOOTSTRAP_INPUT, "type": "date"}),
            "gender": forms.Select(attrs={"class": BOOTSTRAP_SELECT}),
            "profile_image": forms.ClearableFileInput(attrs={"class": BOOTSTRAP_INPUT, "accept": "image/*"}),
            "address": forms.Textarea(attrs={"class": BOOTSTRAP_INPUT, "rows": 3, "placeholder": "Address"}),
            "city": forms.Select(attrs={"class": BOOTSTRAP_SELECT}),
            "emergency_contact_name": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Emergency contact name"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Emergency contact phone"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone and not re.fullmatch(r"[0-9+\-\s()]{7,20}", phone):
            raise ValidationError("Enter a valid phone number.")
        return phone

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get("emergency_contact_phone", "").strip()
        if phone and not re.fullmatch(r"[0-9+\-\s()]{7,20}", phone):
            raise ValidationError("Enter a valid emergency contact phone number.")
        return phone

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        exclude = ("user", "created_at", "updated_at")
        widgets = {
            "address_type": forms.Select(attrs={"class": BOOTSTRAP_SELECT}),
            "label": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Address label"}),
            "address_line1": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "House number, street, area"}),
            "address_line2": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Address line 2 (optional)"}),
            "landmark": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Nearby landmark"}),
            "city": forms.Select(attrs={"class": BOOTSTRAP_SELECT}),
            "postal_code": forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Postal code"}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "is_default": forms.CheckboxInput(attrs={"class": BOOTSTRAP_CHECKBOX}),
        }

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code", "").strip()
        if postal_code and not re.fullmatch(r"[A-Za-z0-9\s-]{3,20}", postal_code):
            raise ValidationError("Enter a valid postal code.")
        return postal_code

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")
        if (latitude is None) != (longitude is None):
            raise ValidationError("Latitude and longitude must both be provided for a map location.")
        if latitude is not None and not Decimal("-90") <= latitude <= Decimal("90"):
            self.add_error("latitude", "Latitude must be between -90 and 90.")
        if longitude is not None and not Decimal("-180") <= longitude <= Decimal("180"):
            self.add_error("longitude", "Longitude must be between -180 and 180.")
        return cleaned_data

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Your name", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Email address", "autocomplete": "email"}),
    )
    mobile_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Mobile number", "autocomplete": "tel"}),
    )
    subject = forms.ChoiceField(
        choices=(
            ("general", "General Enquiry"),
            ("ride", "Ride Support"),
            ("booking", "Booking Issue"),
            ("payment", "Payment Issue"),
            ("account", "Account Support"),
            ("driver", "Driver Support"),
            ("feedback", "Feedback"),
            ("suggestion", "Suggestion"),
            ("complaint", "Complaint"),
            ("other", "Other"),
        ),
        initial="general",
        widget=forms.Select(attrs={"class": BOOTSTRAP_SELECT}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": BOOTSTRAP_INPUT, "rows": 5, "placeholder": "Write your message"}),
    )

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get("mobile_number", "").strip()
        if mobile and not re.fullmatch(r"[0-9+\-\s()]{7,20}", mobile):
            raise ValidationError("Enter a valid mobile number.")
        return mobile

class LoginForm(forms.Form):
    user_id = forms.CharField(required=False, widget=forms.HiddenInput())
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Username or email", "autocomplete": "username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Password", "autocomplete": "current-password", "render_value": False}),
    )

class ForgetPassword(forms.Form):
    email_or_Phone_Number = forms.CharField(
        label="Email or phone number",
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Email or phone number", "autocomplete": "username"}),
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "New password", "autocomplete": "new-password"}),
    )
    new_confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Confirm new password", "autocomplete": "new-password"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("new_confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("new_confirm_password", "Passwords do not match.")
        return cleaned_data

class ResetPassword(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Current password", "autocomplete": "current-password"}),
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "New password", "autocomplete": "new-password"}),
    )
    new_confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Confirm new password", "autocomplete": "new-password"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("new_confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("new_confirm_password", "Passwords do not match.")
        if old_password and new_password and old_password == new_password:
            self.add_error("new_password", "New password must be different from the current password.")
        return cleaned_data

class Booking(forms.Form):
    booking_id = forms.CharField(required=False, widget=forms.HiddenInput())
    pickup_location = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "id": "pickup_location", "placeholder": "Enter pickup location", "autocomplete": "street-address"}),
    )
    destination = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "id": "destination", "placeholder": "Enter destination"}),
    )
    pickup_latitude = forms.DecimalField(
        required=False,
        min_value=Decimal("-90"),
        max_value=Decimal("90"),
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(attrs={"id": "pickup_latitude"}),
    )
    pickup_longitude = forms.DecimalField(
        required=False,
        min_value=Decimal("-180"),
        max_value=Decimal("180"),
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(attrs={"id": "pickup_longitude"}),
    )
    drop_latitude = forms.DecimalField(
        required=False,
        min_value=Decimal("-90"),
        max_value=Decimal("90"),
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(attrs={"id": "drop_latitude"}),
    )
    drop_longitude = forms.DecimalField(
        required=False,
        min_value=Decimal("-180"),
        max_value=Decimal("180"),
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(attrs={"id": "drop_longitude"}),
    )
    ride_type = forms.ModelChoiceField(
        queryset=VehicleType.objects.none(),
        empty_label="Select ride type",
        widget=forms.Select(attrs={"class": BOOTSTRAP_SELECT, "id": "ride_type"}),
    )
    ride_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": BOOTSTRAP_INPUT, "type": "date", "id": "ride_date"}),
    )
    ride_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"class": BOOTSTRAP_INPUT, "type": "time", "id": "ride_time"}),
    )
    ride_status = forms.CharField(required=False, widget=forms.HiddenInput())
    passengers = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=6,
        initial=1,
        widget=forms.NumberInput(attrs={"class": BOOTSTRAP_INPUT, "min": 1, "max": 6}),
    )
    coupon_code = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "id": "coupon_code", "placeholder": "Enter coupon code", "autocomplete": "off"}),
    )
    note = forms.CharField(
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={"class": BOOTSTRAP_INPUT, "rows": 3, "placeholder": "Additional ride instructions"}),
    )
    base_fare = forms.DecimalField(required=False, widget=forms.HiddenInput())
    ride_charge = forms.DecimalField(required=False, widget=forms.HiddenInput())
    distance = forms.DecimalField(required=False, widget=forms.HiddenInput())
    platform_fee = forms.DecimalField(required=False, widget=forms.HiddenInput())
    total_amount = forms.DecimalField(required=False, widget=forms.HiddenInput())
    completed_ride = forms.CharField(required=False, widget=forms.HiddenInput())
    total_ride = forms.CharField(required=False, widget=forms.HiddenInput())
    total_spent = forms.CharField(required=False, widget=forms.HiddenInput())
    fare = forms.DecimalField(required=False, widget=forms.HiddenInput())
    estimate_fare = forms.DecimalField(required=False, widget=forms.HiddenInput())
    your_rating = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ride_type"].queryset = VehicleType.objects.all().order_by("id")
        self.fields["ride_date"].required = False
        self.fields["ride_time"].required = False
        self.fields["passengers"].required = True

    def clean(self):
        cleaned_data = super().clean()
        pickup_lat = cleaned_data.get("pickup_latitude")
        pickup_lng = cleaned_data.get("pickup_longitude")
        drop_lat = cleaned_data.get("drop_latitude")
        drop_lng = cleaned_data.get("drop_longitude")
        if (pickup_lat is None) != (pickup_lng is None):
            self.add_error("pickup_latitude", "Pickup latitude and longitude must both be provided.")
        if (drop_lat is None) != (drop_lng is None):
            self.add_error("drop_latitude", "Drop latitude and longitude must both be provided.")
        if pickup_lat is not None and drop_lat is not None and pickup_lng is not None and drop_lng is not None:
            if pickup_lat == drop_lat and pickup_lng == drop_lng:
                self.add_error("destination", "Pickup and destination cannot be the same location.")
        return cleaned_data

class Payment(forms.Form):
    payment_id = forms.CharField(required=False, widget=forms.HiddenInput())
    payment_type = forms.ChoiceField(
        required=False,
        choices=(("", "Select payment method"),) + tuple(Payment.Method.choices),
        widget=forms.Select(attrs={"class": BOOTSTRAP_SELECT, "id": "payment_type"}),
    )
    payment_date = forms.CharField(required=False, widget=forms.HiddenInput())
    payment_time = forms.CharField(required=False, widget=forms.HiddenInput())
    payment_receipt = forms.CharField(required=False, widget=forms.HiddenInput())

class Driver(forms.Form):
    driver_id = forms.CharField(required=False, widget=forms.HiddenInput())
    driver_name = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Driver name"}))
    driver_phone = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Driver phone"}))
    driver_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Driver email"}))
    driver_registration = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Driver registration"}))
    driver_status = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Driver status"}))
    driver_arrival = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Estimated arrival"}))
    dl_number = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Driving licence number"}))
    vehicle_number = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Vehicle number"}))
    vehicle_insurance = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Vehicle insurance"}))
    vehicle_pollution = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Pollution certificate"}))
    vehicle_type = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Vehicle type"}))
    documnet_upload = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={"class": BOOTSTRAP_INPUT}))

class MyRide(forms.Form):
    ride_id = forms.CharField(required=False, widget=forms.HiddenInput())
    ride_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"class": BOOTSTRAP_INPUT, "type": "date"}))
    ride_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"class": BOOTSTRAP_INPUT, "type": "time"}))
    ride_type = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    ride_track = forms.CharField(required=False, widget=forms.HiddenInput())

class Profile(forms.Form):
    profileimage = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"class": BOOTSTRAP_INPUT, "accept": "image/*"}))
    user_id = forms.CharField(required=False, widget=forms.HiddenInput())
    user_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    first_name = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    last_name = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    country = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    district = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    street = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    village_colony = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    pin_code = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    mobile_number = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": BOOTSTRAP_INPUT}))
    user_type = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    Registration_date = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    Driver_Licence_Number = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    vehicle_type = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    vehicle_number = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    vehicle_insurance = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    vehicle_pollution = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT}))
    documnet_upload = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={"class": BOOTSTRAP_INPUT}))


class UserForm(forms.Form):
    firstname = forms.CharField(
        max_length=150,
        label="First name",
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "First name"})
    )
    lastname = forms.CharField(
        max_length=150,
        label="Last name",
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Last name"})
    )
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Email address"})
    )
    mobilenumber = forms.CharField(
        max_length=20,
        label="Mobile number",
        widget=forms.TextInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Mobile number"})
    )
    gender = forms.ChoiceField(
        choices=[("", "Select gender")] + list(UserProfile.Gender.choices),
        required=False,
        widget=forms.Select(attrs={"class": BOOTSTRAP_SELECT})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Password", "autocomplete": "new-password"})
    )
    confirmpassword = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BOOTSTRAP_INPUT, "placeholder": "Confirm password", "autocomplete": "new-password"})
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if AuthUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_mobilenumber(self):
        mobile = self.cleaned_data["mobilenumber"].strip()
        if not re.fullmatch(r"[0-9+\-\s()]{7,20}", mobile):
            raise ValidationError("Enter a valid mobile number.")
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirmpassword")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirmpassword", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = AuthUser(
            username=self.cleaned_data["email"],
            first_name=self.cleaned_data["firstname"].strip(),
            last_name=self.cleaned_data["lastname"].strip(),
            email=self.cleaned_data["email"]
        )
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            self.save_profile(user)
        return user

    def save_profile(self, user):
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = self.cleaned_data["mobilenumber"]
        profile.gender = self.cleaned_data.get("gender", "")
        profile.save()
        return profile
