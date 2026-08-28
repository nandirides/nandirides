from django import forms
from superuser.models import User 

class superuserForm(forms.Form):
    
    user_id = forms.CharField(
        widget=forms.HiddenInput(attrs={
            'class': 'form-control',
        }))

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username'
        })
    )

