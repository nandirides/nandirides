from datetime import date
from pathlib import Path
from django import forms
from django.core.exceptions import ValidationError
from .models import VehicleType, Vehicle, DriverVehicle, VehicleDocument

class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = [
            "name",
            "code",
            "description",
            "capacity",
            "base_fare",
            "per_km_rate",
            "per_minute_rate",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter vehicle type name",
            }),
            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: SEDAN",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter vehicle type description",
            }),
            "capacity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "base_fare": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "per_km_rate": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "per_minute_rate": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise ValidationError(
                "Vehicle type name must contain at least 2 characters."
            )
        return name

    def clean_code(self):
        code = self.cleaned_data["code"].strip().upper()
        if len(code) < 2:
            raise ValidationError(
                "Vehicle type code must contain at least 2 characters."
            )
        return code

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity <= 0:
            raise ValidationError("Capacity must be greater than 0.")
        return capacity

    def clean_base_fare(self):
        value = self.cleaned_data["base_fare"]
        if value < 0:
            raise ValidationError("Base fare cannot be negative.")
        return value

    def clean_per_km_rate(self):
        value = self.cleaned_data["per_km_rate"]
        if value < 0:
            raise ValidationError("Per KM rate cannot be negative.")
        return value

    def clean_per_minute_rate(self):
        value = self.cleaned_data["per_minute_rate"]
        if value < 0:
            raise ValidationError("Per minute rate cannot be negative.")
        return value


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_number",
            "vehicle_type",
            "brand",
            "model",
            "variant",
            "manufacturing_year",
            "color",
            "fuel_type",
            "seating_capacity",
            "registration_date",
            "registration_expiry",
            "status",
        ]
        widgets = {
            "vehicle_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: UP32AB1234",
            }),
            "vehicle_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "brand": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Maruti",
            }),
            "model": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Swift",
            }),
            "variant": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: VXI",
            }),
            "manufacturing_year": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Example: 2024",
                "min": 1900,
                "max": date.today().year,
            }),
            "color": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: White",
            }),
            "fuel_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "seating_capacity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "registration_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "registration_expiry": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def clean_vehicle_number(self):
        vehicle_number = self.cleaned_data["vehicle_number"].strip().upper()
        if len(vehicle_number) < 4:
            raise ValidationError("Please enter a valid vehicle number.")
        return vehicle_number

    def clean_manufacturing_year(self):
        year = self.cleaned_data.get("manufacturing_year")
        if year:
            current_year = date.today().year
            if year < 1900 or year > current_year:
                raise ValidationError(
                    f"Manufacturing year must be between 1900 and {current_year}."
                )
        return year

    def clean_seating_capacity(self):
        capacity = self.cleaned_data["seating_capacity"]
        if capacity <= 0:
            raise ValidationError("Seating capacity must be greater than 0.")
        return capacity

    def clean(self):
        cleaned_data = super().clean()
        registration_date = cleaned_data.get("registration_date")
        registration_expiry = cleaned_data.get("registration_expiry")
        if registration_date and registration_expiry:
            if registration_expiry <= registration_date:
                self.add_error(
                    "registration_expiry",
                    "Registration expiry date must be after registration date.",
                )
        return cleaned_data


class DriverVehicleForm(forms.ModelForm):
    class Meta:
        model = DriverVehicle
        fields = [
            "driver",
            "vehicle",
            "assigned_from",
            "is_current",
        ]
        widgets = {
            "driver": forms.Select(attrs={
                "class": "form-select",
            }),
            "vehicle": forms.Select(attrs={
                "class": "form-select",
            }),
            "assigned_from": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local",
            }),
            "is_current": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["driver"].queryset = (
            self.fields["driver"].queryset
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
                "driver_code",
            )
        )
        self.fields["vehicle"].queryset = (
            Vehicle.objects.filter(
                status__in=[
                    Vehicle.Status.ACTIVE,
                    Vehicle.Status.INACTIVE,
                ]
            )
            .select_related("vehicle_type")
            .order_by("vehicle_number")
        )

    def clean(self):
        cleaned_data = super().clean()
        driver = cleaned_data.get("driver")
        vehicle = cleaned_data.get("vehicle")
        assigned_from = cleaned_data.get("assigned_from")

        if not driver or not vehicle:
            return cleaned_data

        if assigned_from and self.instance.pk:
            previous_assignment = (
                DriverVehicle.objects
                .filter(pk=self.instance.pk)
                .values_list("assigned_from", flat=True)
                .first()
            )
            if previous_assignment and assigned_from < previous_assignment:
                self.add_error(
                    "assigned_from",
                    "Assigned from date cannot be earlier than the existing assignment date.",
                )

        return cleaned_data


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = [
            "vehicle",
            "document_type",
            "document_number",
            "document_file",
            "issue_date",
            "expiry_date",
            "verification_status",
        ]
        widgets = {
            "vehicle": forms.Select(attrs={
                "class": "form-select",
            }),
            "document_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "document_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter document number",
            }),
            "document_file": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": ".pdf,.jpg,.jpeg,.png",
            }),
            "issue_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "expiry_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "verification_status": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = (
            Vehicle.objects
            .select_related("vehicle_type")
            .order_by("vehicle_number")
        )
        self.fields["verification_status"].choices = [
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ]

    def clean_document_number(self):
        document_number = self.cleaned_data.get(
            "document_number",
            "",
        ).strip()
        return document_number.upper()

    def clean_document_file(self):
        document_file = self.cleaned_data.get("document_file")

        if not document_file:
            if self.instance and self.instance.pk:
                return self.instance.document_file
            raise ValidationError("Please upload a document file.")

        allowed_extensions = {
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
        }

        extension = Path(document_file.name).suffix.lower()

        if extension not in allowed_extensions:
            raise ValidationError(
                "Only PDF, JPG, JPEG and PNG files are allowed."
            )

        max_size = 5 * 1024 * 1024

        if document_file.size > max_size:
            raise ValidationError(
                "Document file size must not exceed 5 MB."
            )

        return document_file

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get("issue_date")
        expiry_date = cleaned_data.get("expiry_date")

        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                self.add_error(
                    "expiry_date",
                    "Expiry date must be after issue date.",
                )

        return cleaned_data
