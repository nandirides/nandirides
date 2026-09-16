from django import forms
from .models import (
    Driver,
    DriverDocument,
    DriverBankAccount,
)
# ============================================================
# DRIVER FORM
# ============================================================
class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "user",
            "driver_code",
            "license_number",
            "license_expiry",
            "experience_years",
            "status",
            "verification_status",
        ]
        widgets = {
            "user": forms.Select(attrs={
                "class": "form-select",
            }),
            "driver_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Driver code",
            }),
            "license_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "License number",
            }),
            "license_expiry": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "experience_years": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Experience in years",
                "min": "0",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "verification_status": forms.Select(attrs={
                "class": "form-select",
            }),
        }
        labels = {
            "user": "User",
            "driver_code": "Driver Code",
            "license_number": "License Number",
            "license_expiry": "License Expiry",
            "experience_years": "Experience Years",
            "status": "Status",
            "verification_status": "Verification Status",
        }
        help_texts = {
            "user": "Select the user who will be registered as a driver.",
            "driver_code": "Unique driver identification code.",
            "license_number": "Driver's unique driving license number.",
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].required = True
        self.fields["driver_code"].required = True
        self.fields["license_number"].required = True
# ============================================================
# DRIVER DOCUMENT FORM
# ============================================================
class DriverDocumentForm(forms.ModelForm):
    class Meta:
        model = DriverDocument
        fields = [
            "driver",
            "document_type",
            "document_number",
            "document_file",
            "issue_date",
            "expiry_date",
        ]
        widgets = {
            "driver": forms.Select(attrs={
                "class": "form-select",
            }),
            "document_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "document_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Document number",
            }),
            "document_file": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "issue_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "expiry_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["document_file"].help_text = (
            "Upload the required driver document."
        )
    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get("issue_date")
        expiry_date = cleaned_data.get("expiry_date")
        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                self.add_error(
                    "expiry_date",
                    "Expiry date must be after the issue date."
                )
        return cleaned_data
# ============================================================
# DRIVER BANK ACCOUNT FORM
# ============================================================
class DriverBankAccountForm(forms.ModelForm):
    class Meta:
        model = DriverBankAccount
        fields = [
            "driver",
            "account_holder_name",
            "account_number",
            "ifsc_code",
            "bank_name",
            "upi_id",
            "is_primary",
        ]
        widgets = {
            "driver": forms.Select(attrs={
                "class": "form-select",
            }),
            "account_holder_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Account holder name",
            }),
            "account_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Bank account number",
            }),
            "ifsc_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "IFSC code",
                "style": "text-transform: uppercase;",
            }),
            "bank_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Bank name",
            }),
            "upi_id": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "UPI ID (optional)",
            }),
            "is_primary": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }
    def clean_ifsc_code(self):
        ifsc = self.cleaned_data.get("ifsc_code")
        if ifsc:
            ifsc = ifsc.strip().upper()
        return ifsc
    def clean_account_number(self):
        account_number = self.cleaned_data.get("account_number")
        if account_number:
            account_number = account_number.strip()
        return account_number
    def clean(self):
        cleaned_data = super().clean()
        driver = cleaned_data.get("driver")
        is_primary = cleaned_data.get("is_primary")
        if driver and is_primary:
            qs = DriverBankAccount.objects.filter(
                driver=driver,
                is_primary=True,
            )
            if self.instance and self.instance.pk:
                qs = qs.exclude(
                    pk=self.instance.pk
                )
            if qs.exists():
                self.add_error(
                    "is_primary",
                    "This driver already has a primary bank account."
                )
        return cleaned_data