from django import forms
from .models import FareRule, SurgePricing

class FareRuleForm(forms.ModelForm):
    class Meta:
        model = FareRule
        fields = [
            "vehicle_type",
            "city",
            "base_fare",
            "minimum_fare",
            "per_km_rate",
            "per_minute_rate",
            "waiting_charge",
            "cancellation_charge",
            "effective_from",
            "effective_to",
            "is_active",
        ]
        widgets = {
            "vehicle_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "city": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "base_fare": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter base fare",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "minimum_fare": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter minimum fare",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "per_km_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter per KM rate",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "per_minute_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter per minute rate",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "waiting_charge": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter waiting charge",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "cancellation_charge": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter cancellation charge",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "effective_from": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "effective_to": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        base_fare = cleaned_data.get("base_fare")
        minimum_fare = cleaned_data.get("minimum_fare")
        effective_from = cleaned_data.get("effective_from")
        effective_to = cleaned_data.get("effective_to")
        if (
            base_fare is not None
            and minimum_fare is not None
            and minimum_fare < base_fare
        ):
            self.add_error(
                "minimum_fare",
                "Minimum fare cannot be less than base fare.",
            )
        if (
            effective_from
            and effective_to
            and effective_to <= effective_from
        ):
            self.add_error(
                "effective_to",
                "Effective to must be later than effective from.",
            )
        return cleaned_data


class SurgePricingForm(forms.ModelForm):
    class Meta:
        model = SurgePricing
        fields = [
            "city",
            "vehicle_type",
            "multiplier",
            "start_time",
            "end_time",
            "reason",
            "is_active",
        ]
        widgets = {
            "city": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "vehicle_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "multiplier": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 1.50",
                    "step": "0.01",
                    "min": "1",
                }
            ),
            "start_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "end_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "reason": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter surge reason",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        multiplier = cleaned_data.get("multiplier")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if multiplier is not None and multiplier < 1:
            self.add_error(
                "multiplier",
                "Surge multiplier cannot be less than 1.00.",
            )
        if (
            start_time
            and end_time
            and end_time <= start_time
        ):
            self.add_error(
                "end_time",
                "End time must be later than start time.",
            )
        return cleaned_data