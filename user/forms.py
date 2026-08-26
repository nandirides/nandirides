from django import forms
from user.models import User 

class LoginForm(forms.Form):
    
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

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )

class profile(forms.Form):
    
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

    firstname = forms.CharField(
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Firstname'
            })
        )

    lastname = forms.CharField(
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Lastname'
            })
        )
    
    
class UserForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    class Meta:
        model = User
        fields = ['username', 'firstname', 'lastname', 'password', 'email',
                  'gender', 'dob']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter User Name'
            }),
            'firstname': forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Enter First Name'
                        }),
            'lastname': forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Enter Last Name'
                        }),
            'password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter User Password'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email Id'
            }),
            'dob': forms.DateInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'DD/MM/YYYY'
                        }),
        }
