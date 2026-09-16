from django import forms
from django.contrib.auth import get_user_model
from .models import SupportCategory, SupportTicket
User = get_user_model()
class SupportCategoryForm(forms.ModelForm):
    class Meta:
        model = SupportCategory
        fields = [
            "name",
            "description",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter support category name",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter category description",
                "rows": 4,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }
        labels = {
            "name": "Category Name",
            "description": "Description",
            "is_active": "Active Category",
        }
        help_texts = {
            "name": "Enter a unique support category name.",
            "description": "Briefly describe this support category.",
            "is_active": "Inactive categories will not be available for new tickets.",
        }
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name:
            name = name.strip()
        return name
class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = [
            "ticket_number",
            "user",
            "ride",
            "category",
            "subject",
            "description",
            "priority",
            "status",
            "assigned_to",
        ]
        widgets = {
            "ticket_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "NR-SUP-0001",
            }),
            "user": forms.Select(attrs={
                "class": "form-select",
            }),
            "ride": forms.Select(attrs={
                "class": "form-select",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter ticket subject",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Describe the issue in detail...",
                "rows": 6,
            }),
            "priority": forms.Select(attrs={
                "class": "form-select",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "assigned_to": forms.Select(attrs={
                "class": "form-select",
            }),
        }
        labels = {
            "ticket_number": "Ticket Number",
            "user": "Customer",
            "ride": "Related Ride",
            "category": "Category",
            "subject": "Subject",
            "description": "Description",
            "priority": "Priority",
            "status": "Status",
            "assigned_to": "Assigned To",
        }
        help_texts = {
            "ticket_number": "Unique support ticket number.",
            "ride": "Optional: Link this ticket to a ride.",
            "assigned_to": "Select the support/admin user responsible for this ticket.",
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = SupportCategory.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["user"].queryset = User.objects.filter(
            is_active=True
        ).order_by("first_name", "last_name", "username")
        self.fields["assigned_to"].queryset = User.objects.filter(
            is_active=True
        ).order_by("first_name", "last_name", "username")
        self.fields["ride"].required = False
        self.fields["assigned_to"].required = False
    def clean_ticket_number(self):
        ticket_number = self.cleaned_data.get("ticket_number")
        if ticket_number:
            ticket_number = ticket_number.strip().upper()
        return ticket_number
    def clean_subject(self):
        subject = self.cleaned_data.get("subject")
        if subject:
            subject = subject.strip()
        return subject
    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description:
            description = description.strip()
        return description