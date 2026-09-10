from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from dashboard.models import Gallery


class UserCreateForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email address",
        })
    )

    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "First name",
        })
    )

    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Last name",
        })
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

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Username",
        })

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password",
        })

    def clean_username(self):
        username = self.cleaned_data.get("username")

        qs = User.objects.filter(username=username)

        # UPDATE:
        # Don't consider the current user as a duplicate.
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
    
    class Meta:
        model = Gallery
        fields =[
            'profile_image'
        ]
        
        help_texts = {
            'profile_image' : 'Optional: Upload a profile image',
            'my_file' : 'Optional: Attach any addational document (PDF, DOCX,etc.)'
        }
        