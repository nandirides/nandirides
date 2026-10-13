from django import forms
from .models import Country, State, City, Location
class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ["name", "code"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter country name",
                }
            ),
            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter country code",
                    "maxlength": "10",
                }
            ),
        }
    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Country name is required.")
        return name
    def clean_code(self):
        code = self.cleaned_data["code"].strip().upper()
        if not code:
            raise forms.ValidationError("Country code is required.")
        return code
class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ["country", "name"]
        widgets = {
            "country": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter state name",
                }
            ),
        }
    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("State name is required.")
        return name
class CityForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by("name"),
        required=True,
        empty_label="Select Country",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_country",
            }
        ),
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        required=True,
        empty_label="Select State",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_state",
            }
        ),
    )
    class Meta:
        model = City
        fields = ["country", "state", "name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter city name",
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            selected_state = self.instance.state
            selected_country = selected_state.country
            self.initial["country"] = selected_country.pk
            self.initial["state"] = selected_state.pk
            self.fields["state"].queryset = State.objects.filter(
                country=selected_country
            ).order_by("name")
        elif self.data:
            country_id = self.data.get("country")
            state_id = self.data.get("state")
            if country_id:
                self.fields["state"].queryset = State.objects.filter(
                    country_id=country_id
                ).order_by("name")
            elif state_id:
                self.fields["state"].queryset = State.objects.filter(
                    pk=state_id
                ).order_by("name")
    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        state = cleaned_data.get("state")
        if country and state and state.country_id != country.id:
            self.add_error(
                "state",
                "Selected state does not belong to the selected country.",
            )
        return cleaned_data
    def save(self, commit=True):
        city = super().save(commit=False)
        if commit:
            city.save()
        return city
class LocationForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by("name"),
        required=True,
        empty_label="Select Country",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_country",
            }
        ),
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        required=True,
        empty_label="Select State",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_state",
            }
        ),
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False,
        empty_label="Select City",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_city",
            }
        ),
    )
    class Meta:
        model = Location
        fields = [
            "country",
            "state",
            "city",
            "address",
            "latitude",
            "longitude",
        ]
        widgets = {
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter location address",
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter latitude",
                    "step": "any",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter longitude",
                    "step": "any",
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.city:
            selected_state = self.instance.city.state
            selected_country = selected_state.country
            self.fields["state"].queryset = State.objects.filter(
                country=selected_country
            ).order_by("name")
            self.fields["city"].queryset = City.objects.filter(
                state=selected_state
            ).order_by("name")
            self.initial["country"] = selected_country.pk
            self.initial["state"] = selected_state.pk
            self.initial["city"] = self.instance.city.pk
        elif self.data:
            country_id = self.data.get("country")
            state_id = self.data.get("state")
            if country_id:
                self.fields["state"].queryset = State.objects.filter(
                    country_id=country_id
                ).order_by("name")
            if state_id:
                self.fields["city"].queryset = City.objects.filter(
                    state_id=state_id
                ).order_by("name")
    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        state = cleaned_data.get("state")
        city = cleaned_data.get("city")
        if country and state and state.country_id != country.id:
            self.add_error(
                "state",
                "Selected state does not belong to the selected country.",
            )
        if state and city and city.state_id != state.id:
            self.add_error(
                "city",
                "Selected city does not belong to the selected state.",
            )
        return cleaned_data
