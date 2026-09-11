from django import forms
from user.models import User 

class ContactForm(forms.Form):

    name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your full name"
            }
        )
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email"
            }
        )
    )

    mobile_number = forms.CharField(
        label="Mobile Number",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter mobile number"
            }
        )
    )

    subject = forms.CharField(
        label="Subject",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "What can we help you with?"
            }
        )
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Write your message here...",
                "rows": 5
            }
        )
    )

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

class ForgetPassword(forms.Form):

    # user_id = forms.CharField(
    #     widget=forms.HiddenInput(attrs={
    #         'class': 'form-control',
    #     }))

    email_or_Phone_Number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email or Phone Number'
        })
        )

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter New Password'
        })
        )
    
    new_confirm_password = forms.CharField(
            widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter New Confirm Password'
            })
            )


class ResetPassword(forms.Form):

    # user_id = forms.CharField(
    #     widget=forms.HiddenInput(attrs={
    #         'class': 'form-control',
    #     }))

    old_password = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Old Password'
        })
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter New Password'
        })
        )
    
    new_confirm_password = forms.CharField(
            widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter New Confirm Password'
            })
            )

class Booking(forms.Form):
    booking_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={
            'value': '1'
        })
    )
    pickup_location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'pickup_location',
            'placeholder': 'Enter pickup location',
            'required': True
        })
    )
    destination = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'destination',
            'placeholder': 'Enter destination',
            'required': True
        })
    )
    ride_type = forms.ChoiceField(
        choices=[
            ('Bike', 'Bike'),
            ('Auto', 'Auto'),
            ('Sedan', 'Sedan')
        ],
        required=True
    )
    ride_date = forms.CharField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'id': 'ride_date',
            'type': 'date',
            'required': True
        })
    )
    ride_time = forms.CharField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'id': 'ride_time',
            'type': 'time',
            'required': True
        })
    )
    ride_status = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    passengers = forms.IntegerField(
        min_value=1,
        max_value=6,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'passengers',
            'min': '1',
            'max': '6',
            'required': True
        })
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'note',
            'placeholder': 'Any special request?',
            'rows': 3
        })
    )
    base_fare = forms.CharField(required=False, widget=forms.HiddenInput())
    ride_charge = forms.CharField(required=False, widget=forms.HiddenInput())
    distance = forms.CharField(required=False, widget=forms.HiddenInput())
    platform_fee = forms.CharField(required=False, widget=forms.HiddenInput())
    total_amount = forms.CharField(required=False, widget=forms.HiddenInput())
    completed_ride = forms.CharField(required=False, widget=forms.HiddenInput())
    total_ride = forms.CharField(required=False, widget=forms.HiddenInput())
    total_spent = forms.CharField(required=False, widget=forms.HiddenInput())
    fare = forms.CharField(required=False, widget=forms.HiddenInput())
    estimate_fare = forms.CharField(required=False, widget=forms.HiddenInput())
    your_rating = forms.CharField(required=False, widget=forms.HiddenInput())
    
class Payment(forms.Form):
    payment_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    payment_type = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    payment_date = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    payment_time = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    payment_receipt = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

class Driver(forms.Form):
    driver_id = forms.CharField(
        widget=forms.HiddenInput(attrs={
        })
        )


    driver_name = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    driver_phone = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    driver_email = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    driver_registration = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    driver_status = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    driver_arrival = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    dl_number = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    vehicle_number = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    vehicle_insurance = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    vehicle_pollution = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    vehicle_type = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    documnet_upload = forms.FileField(
                        widget=forms.ClearableFileInput(attrs={
                        })
                    )   
    

class MyRide(forms.Form):
    ride_id = forms.CharField(
        widget=forms.HiddenInput(attrs={
        })
        )


    ride_date = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    ride_time = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    ride_type = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )


    ride_track = forms.CharField(
            widget=forms.TextInput(attrs={
            })
        )



class Profile(forms.Form):

    profileimage = forms.ImageField(
                widget=forms.ClearableFileInput(attrs={
                    'class': 'form-control logo'
                })
            )
        
    user_id = forms.CharField(
        widget=forms.HiddenInput(attrs={
            'class': 'form-control',
        })
        )

    user_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control input-field rounded shadow',
            'placeholder': 'Enter User Name'
        })
    )

    first_name = forms.CharField(
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter First Name'
            })
        )

    last_name = forms.CharField(
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Last Name'
            })
        )
    country = forms.ChoiceField(
                choices=[('', 'Please Select One')] + User.COUNTRY_CHOICES,
                widget=forms.Select(attrs={
                'class': 'form-control input-field rounded shadow'
                }),
        )
    state = forms.ChoiceField(
                choices=[('', 'Please Select One')] + User.STATE_CHOICES,
                widget=forms.Select(attrs={
                'class': 'form-control input-field rounded shadow'
                }),
            )
    district = forms.ChoiceField(
                choices=[('', 'Please Select One')] + User.DISTRICT_CHOICES,
                widget=forms.Select(attrs={
                'class': 'form-control input-field rounded shadow'
                }),
            )
    
    
    street = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Street or House Number'
                })
            )
    
    village_colony = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Village and Colony Name'
                })
            )
    
    pin_code = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Pin Code'
                })
            )
    
    mobile_number = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Mobile Number'
                })
            )
    email = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter email'
                })
            )

    user_type = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'User Type'
                })
            )

    Registration_date = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Registration Date'
                    })
                )

    Driver_Licence_Number = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Driver Licence Number'
                    })
                )

    vehicle_type = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Vehicle Type'
                    })
                )

    vehicle_number = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Vehicle Number'
                    })
                )

    vehicle_insurance = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Vehicle Insurance'
                    })
                )

    vehicle_pollution = forms.CharField(
                        widget=forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Vehicle Pollution'
                        })
                    )

    documnet_upload = forms.FileField(
                        widget=forms.ClearableFileInput(attrs={
                            'class': 'form-control'
                        })
                    )   
    
class UserForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.RadioSelect(attrs={
                'class': 'd-flex gap-4 input-field'
                }),
        required=True
    )
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'mobilenumber',
                  'gender', 'password', 'confirmpassword',]

        widgets = {
            'firstname': forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Enter First Name'
                        }),
            'lastname': forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Enter Last Name'
                        }),
            'mobilenumber': forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Enter Mobile Number'
                        }),
            'password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Password'
            }),
            'confirmpassword': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Confirm Password'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email Id'
            }),
        }
