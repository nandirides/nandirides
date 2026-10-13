from django import forms
from .models import Refund
class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = [
            "refund_amount",
            "reason",
            "refund_reference",
            "status",
            "processed_at",
        ]
        widgets = {
            "refund_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter refund amount",
                "step": "0.01",
                "min": "0.01",
            }),
            "reason": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter refund reason",
                "rows": 4,
            }),
            "refund_reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter refund reference",
            }),
            "status": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Pending / Processed / Failed",
            }),
            "processed_at": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local",
            }),
        }
    def __init__(self,*args,**kwargs):
        self.payment = kwargs.pop("payment",None)
        super().__init__(*args,**kwargs)
    def clean_refund_amount(self):
        refund_amount = self.cleaned_data["refund_amount"]
        if refund_amount <= 0:
            raise forms.ValidationError("Refund amount must be greater than zero.")
        if self.payment and refund_amount > self.payment.amount:
            raise forms.ValidationError(
                f"Refund amount cannot be greater than payment amount ₹{self.payment.amount}."
            )
        return refund_amount