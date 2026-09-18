from django import forms
from .models import Coupon
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            "code",
            "name",
            "discount_type",
            "discount_value",
            "maximum_discount",
            "minimum_fare",
            "usage_limit",
            "per_user_limit",
            "valid_from",
            "valid_to",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter coupon code",
                "style": "text-transform: uppercase;"
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter coupon name"
            }),
            "discount_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "discount_value": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter discount value",
                "step": "0.01",
                "min": "0"
            }),
            "maximum_discount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter maximum discount",
                "step": "0.01",
                "min": "0"
            }),
            "minimum_fare": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter minimum fare",
                "step": "0.01",
                "min": "0"
            }),
            "usage_limit": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Leave blank for unlimited",
                "min": "1"
            }),
            "per_user_limit": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter per user limit",
                "min": "1"
            }),
            "valid_from": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local"
            }),
            "valid_to": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }
    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code:
            code = code.strip().upper()
        return code
    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get("discount_type")
        discount_value = cleaned_data.get("discount_value")
        maximum_discount = cleaned_data.get("maximum_discount")
        minimum_fare = cleaned_data.get("minimum_fare")
        usage_limit = cleaned_data.get("usage_limit")
        per_user_limit = cleaned_data.get("per_user_limit")
        valid_from = cleaned_data.get("valid_from")
        valid_to = cleaned_data.get("valid_to")
        if discount_value is not None and discount_value < 0:
            self.add_error("discount_value", "Discount value cannot be negative.")
        if discount_type == Coupon.DiscountType.PERCENTAGE and discount_value is not None:
            if discount_value > 100:
                self.add_error("discount_value", "Percentage discount cannot be greater than 100%.")
        if maximum_discount is not None and maximum_discount < 0:
            self.add_error("maximum_discount", "Maximum discount cannot be negative.")
        if minimum_fare is not None and minimum_fare < 0:
            self.add_error("minimum_fare", "Minimum fare cannot be negative.")
        if usage_limit is not None and usage_limit < 1:
            self.add_error("usage_limit", "Usage limit must be at least 1.")
        if per_user_limit is not None and per_user_limit < 1:
            self.add_error("per_user_limit", "Per user limit must be at least 1.")
        if valid_from and valid_to and valid_to <= valid_from:
            self.add_error("valid_to", "Valid to must be later than valid from.")
        return cleaned_data