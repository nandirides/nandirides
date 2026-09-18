from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from dashboard.models import Gallery, UserProfile, UserAddress
from locations.models import City


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }
        ),
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Mobile number",
                "maxlength": "20",
            }
        ),
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )
    gender = forms.ChoiceField(
        required=False,
        choices=UserProfile.Gender.choices,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    city = forms.ModelChoiceField(
        required=False,
        queryset=City.objects.none(),
        empty_label="Select city",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Enter profile address",
                "rows": 3,
            }
        ),
    )
    emergency_contact_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Emergency contact name",
            }
        ),
    )
    emergency_contact_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Emergency contact phone",
                "maxlength": "20",
            }
        ),
    )
    address_type = forms.ChoiceField(
        required=False,
        choices=UserAddress.AddressType.choices,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    label = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Example: Home, Office",
            }
        ),
    )
    address_line1 = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Address line 1",
            }
        ),
    )
    address_line2 = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Address line 2",
            }
        ),
    )
    landmark = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Landmark",
            }
        ),
    )
    postal_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Postal code",
                "maxlength": "20",
            }
        ),
    )
    address_city = forms.ModelChoiceField(
        required=False,
        queryset=City.objects.none(),
        empty_label="Select address city",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cities = City.objects.all().order_by("name")
        self.fields["city"].queryset = cities
        self.fields["address_city"].queryset = cities
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Username",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Confirm password",
            }
        )
        if self.instance and self.instance.pk:
            self.fields["username"].disabled = True
            self.fields["password1"].required = False
            self.fields["password2"].required = False
            self.fields["password1"].help_text = (
                "Leave blank to keep the current password."
            )
            try:
                profile = self.instance.profile
            except UserProfile.DoesNotExist:
                profile = None
            address = (
                UserAddress.objects.filter(
                    user=self.instance,
                    is_default=True,
                ).first()
                or UserAddress.objects.filter(
                    user=self.instance,
                ).first()
            )
            if profile:
                self.fields["phone"].initial = profile.phone
                self.fields["date_of_birth"].initial = profile.date_of_birth
                self.fields["gender"].initial = profile.gender
                self.fields["city"].initial = profile.city
                self.fields["address"].initial = profile.address
                self.fields["emergency_contact_name"].initial = (
                    profile.emergency_contact_name
                )
                self.fields["emergency_contact_phone"].initial = (
                    profile.emergency_contact_phone
                )
                self.fields["profile_image"].initial = profile.profile_image
            if address:
                self.fields["address_type"].initial = address.address_type
                self.fields["label"].initial = address.label
                self.fields["address_line1"].initial = address.address_line1
                self.fields["address_line2"].initial = address.address_line2
                self.fields["landmark"].initial = address.landmark
                self.fields["postal_code"].initial = address.postal_code
                self.fields["address_city"].initial = address.city
    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "A user with that username already exists."
            )
        return username


class GalleryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_image"].required = True
        self.fields["category"].required = True

    class Meta:
        model = Gallery
        fields = [
            "profile_image",
            "category",
        ]
        widgets = {
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }
        help_texts = {
            "profile_image": "Upload one gallery image",
            "category": "Select image category",
        }