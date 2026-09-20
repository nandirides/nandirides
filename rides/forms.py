from django import forms
from django.db.models import Q

from .models import (
    CancellationReason,
    Ride,
    RideCancellation,
    RideDriverAssignment,
    RideRating,
    RideRequest,
    RideStop,
    RideTracking,
)
from drivers.models import Driver
from locations.models import Location
from vehicles.models import Vehicle


class RideRequestForm(forms.ModelForm):
    class Meta:
        model = RideRequest
        fields = [
            "request_number",
            "passenger",
            "pickup_location",
            "drop_location",
            "vehicle_type",
            "scheduled_at",
            "estimated_distance",
            "estimated_duration",
            "estimated_fare",
            "status",
        ]
        widgets = {
            "request_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter request number",
                }
            ),
            "passenger": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "pickup_location": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "drop_location": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "vehicle_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "scheduled_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "estimated_distance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "estimated_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "0",
                }
            ),
            "estimated_fare": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        pickup = cleaned_data.get("pickup_location")
        drop = cleaned_data.get("drop_location")
        distance = cleaned_data.get("estimated_distance")
        duration = cleaned_data.get("estimated_duration")
        fare = cleaned_data.get("estimated_fare")

        if pickup and drop and pickup == drop:
            self.add_error(
                "drop_location",
                "Pickup and drop location cannot be the same.",
            )

        if distance is not None and distance < 0:
            self.add_error(
                "estimated_distance",
                "Distance cannot be negative.",
            )

        if duration is not None and duration < 0:
            self.add_error(
                "estimated_duration",
                "Duration cannot be negative.",
            )

        if fare is not None and fare < 0:
            self.add_error(
                "estimated_fare",
                "Fare cannot be negative.",
            )

        return cleaned_data


class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            "ride_number",
            "ride_request",
            "passenger",
            "driver",
            "vehicle",
            "pickup_location",
            "drop_location",
            "scheduled_at",
            "distance_km",
            "duration_minutes",
            "status",
        ]
        widgets = {
            "ride_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter ride number",
                }
            ),
            "ride_request": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "passenger": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "driver": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "vehicle": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "pickup_location": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "drop_location": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "scheduled_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "distance_km": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "duration_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "0",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_request_id = (
            self.instance.ride_request_id
            if self.instance.pk
            else None
        )

        self.fields["ride_request"].queryset = (
            RideRequest.objects
            .select_related(
                "passenger",
                "vehicle_type",
                "pickup_location",
                "drop_location",
            )
            .filter(
                Q(ride__isnull=True) | Q(pk=current_request_id)
            )
            .order_by("-requested_at")
        )

        self.fields["driver"].queryset = (
            Driver.objects
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
                "driver_code",
            )
        )

        self.fields["vehicle"].queryset = (
            Vehicle.objects
            .select_related("vehicle_type")
            .order_by("vehicle_number")
        )

        self.fields["passenger"].queryset = (
            self.fields["passenger"].queryset.order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        self.fields["pickup_location"].queryset = (
            Location.objects.all().order_by("address")
        )

        self.fields["drop_location"].queryset = (
            Location.objects.all().order_by("address")
        )

        self.fields["ride_request"].empty_label = "Select ride request"
        self.fields["passenger"].empty_label = "Select passenger"
        self.fields["driver"].empty_label = "Select driver"
        self.fields["vehicle"].empty_label = "Select vehicle"
        self.fields["pickup_location"].empty_label = "Select pickup location"
        self.fields["drop_location"].empty_label = "Select drop location"

        self.fields["pickup_location"].label_from_instance = (
            lambda obj: obj.address or f"Location #{obj.pk}"
        )

        self.fields["drop_location"].label_from_instance = (
            lambda obj: obj.address or f"Location #{obj.pk}"
        )

    def clean(self):
        cleaned_data = super().clean()

        ride_request = cleaned_data.get("ride_request")
        passenger = cleaned_data.get("passenger")
        driver = cleaned_data.get("driver")
        vehicle = cleaned_data.get("vehicle")
        pickup = cleaned_data.get("pickup_location")
        drop = cleaned_data.get("drop_location")
        distance = cleaned_data.get("distance_km")
        duration = cleaned_data.get("duration_minutes")

        if ride_request:
            if passenger and passenger != ride_request.passenger:
                self.add_error(
                    "passenger",
                    "Passenger must match the selected ride request.",
                )

            if pickup and pickup != ride_request.pickup_location:
                self.add_error(
                    "pickup_location",
                    "Pickup location must match the selected ride request.",
                )

            if drop and drop != ride_request.drop_location:
                self.add_error(
                    "drop_location",
                    "Drop location must match the selected ride request.",
                )

            if (
                vehicle
                and ride_request.vehicle_type
                and vehicle.vehicle_type_id != ride_request.vehicle_type_id
            ):
                self.add_error(
                    "vehicle",
                    "Selected vehicle must match the ride request vehicle type.",
                )

        if pickup and drop and pickup == drop:
            self.add_error(
                "drop_location",
                "Pickup and drop location cannot be the same.",
            )

        if distance is not None and distance < 0:
            self.add_error(
                "distance_km",
                "Distance cannot be negative.",
            )

        if duration is not None and duration < 0:
            self.add_error(
                "duration_minutes",
                "Duration cannot be negative.",
            )

        return cleaned_data


class RideStatusForm(forms.Form):
    status = forms.ChoiceField(
        label="Ride Status",
        choices=Ride.Status.choices,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    def __init__(
        self,
        *args,
        current_status=None,
        allowed_statuses=None,
        **kwargs,
    ):
        kwargs.pop("instance", None)

        super().__init__(*args, **kwargs)

        if allowed_statuses:
            allowed_values = {
                value
                for value, label in allowed_statuses
            }

            self.fields["status"].choices = [
                (value, label)
                for value, label in Ride.Status.choices
                if value in allowed_values
            ]

        if current_status:
            self.initial["status"] = current_status

    def clean_status(self):
        value = self.cleaned_data.get("status")

        valid_statuses = {
            choice[0]
            for choice in self.fields["status"].choices
        }

        if value not in valid_statuses:
            raise forms.ValidationError(
                "Please select a valid ride status."
            )

        return value


class RideStopForm(forms.ModelForm):
    class Meta:
        model = RideStop
        fields = [
            "ride",
            "stop_order",
            "location",
            "arrival_time",
            "departure_time",
            "status",
        ]
        widgets = {
            "ride": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "stop_order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Enter stop order",
                }
            ),
            "location": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "arrival_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "departure_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["location"].queryset = (
            Location.objects.all().order_by("address")
        )

        self.fields["location"].empty_label = "Select location"

        self.fields["location"].label_from_instance = (
            lambda obj: obj.address or f"Location #{obj.pk}"
        )

    def clean_stop_order(self):
        value = self.cleaned_data.get("stop_order")

        if value is not None and value < 1:
            raise forms.ValidationError(
                "Stop order must be at least 1."
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        arrival_time = cleaned_data.get("arrival_time")
        departure_time = cleaned_data.get("departure_time")

        if (
            arrival_time
            and departure_time
            and departure_time < arrival_time
        ):
            self.add_error(
                "departure_time",
                "Departure time cannot be earlier than arrival time.",
            )

        return cleaned_data


class RideDriverAssignmentForm(forms.ModelForm):
    class Meta:
        model = RideDriverAssignment
        fields = [
            "ride",
            "driver",
            "status",
            "accepted_at",
            "rejected_at",
            "rejection_reason",
        ]
        widgets = {
            "ride": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "driver": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "accepted_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "rejected_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "rejection_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter rejection reason",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["driver"].queryset = (
            Driver.objects
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
                "driver_code",
            )
        )

        self.fields["driver"].empty_label = "Select driver"

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        accepted_at = cleaned_data.get("accepted_at")
        rejected_at = cleaned_data.get("rejected_at")
        rejection_reason = cleaned_data.get("rejection_reason")

        if (
            status == RideDriverAssignment.Status.ACCEPTED
            and not accepted_at
        ):
            self.add_error(
                "accepted_at",
                "Accepted time is required when assignment is accepted.",
            )

        if status == RideDriverAssignment.Status.REJECTED:
            if not rejected_at:
                self.add_error(
                    "rejected_at",
                    "Rejected time is required when assignment is rejected.",
                )

            if not rejection_reason:
                self.add_error(
                    "rejection_reason",
                    "Rejection reason is required when assignment is rejected.",
                )

        if status != RideDriverAssignment.Status.REJECTED:
            cleaned_data["rejection_reason"] = (
                cleaned_data.get("rejection_reason") or ""
            )

        return cleaned_data


class RideTrackingForm(forms.ModelForm):
    class Meta:
        model = RideTracking
        fields = [
            "ride",
            "driver",
            "latitude",
            "longitude",
            "speed",
            "heading",
            "accuracy",
        ]
        widgets = {
            "ride": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "driver": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.000001",
                    "placeholder": "e.g. 26.8467",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.000001",
                    "placeholder": "e.g. 80.9462",
                }
            ),
            "speed": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "km/h",
                }
            ),
            "heading": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "360",
                    "placeholder": "0 - 360",
                }
            ),
            "accuracy": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Accuracy in meters",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["driver"].queryset = (
            Driver.objects
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
                "driver_code",
            )
        )

        self.fields["driver"].empty_label = "Select driver"

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")
        speed = cleaned_data.get("speed")
        heading = cleaned_data.get("heading")
        accuracy = cleaned_data.get("accuracy")

        if latitude is not None and not -90 <= latitude <= 90:
            self.add_error(
                "latitude",
                "Latitude must be between -90 and 90.",
            )

        if longitude is not None and not -180 <= longitude <= 180:
            self.add_error(
                "longitude",
                "Longitude must be between -180 and 180.",
            )

        if speed is not None and speed < 0:
            self.add_error(
                "speed",
                "Speed cannot be negative.",
            )

        if heading is not None and not 0 <= heading <= 360:
            self.add_error(
                "heading",
                "Heading must be between 0 and 360.",
            )

        if accuracy is not None and accuracy < 0:
            self.add_error(
                "accuracy",
                "Accuracy cannot be negative.",
            )

        return cleaned_data


class CancellationReasonForm(forms.ModelForm):
    class Meta:
        model = CancellationReason
        fields = [
            "type",
            "reason",
            "charge_applicable",
            "charge_amount",
            "is_active",
        ]
        widgets = {
            "type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "reason": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter cancellation reason",
                }
            ),
            "charge_applicable": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "charge_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
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

        charge_applicable = cleaned_data.get("charge_applicable")
        charge_amount = cleaned_data.get("charge_amount")

        if charge_applicable and (
            charge_amount is None or charge_amount <= 0
        ):
            self.add_error(
                "charge_amount",
                "Enter a valid cancellation charge.",
            )

        if not charge_applicable:
            cleaned_data["charge_amount"] = 0

        return cleaned_data


class RideCancellationForm(forms.ModelForm):
    class Meta:
        model = RideCancellation
        fields = [
            "ride",
            "cancelled_by",
            "reason",
            "reason_text",
            "cancellation_charge",
        ]
        widgets = {
            "ride": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "cancelled_by": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "reason": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "reason_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter additional details",
                }
            ),
            "cancellation_charge": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["reason"].queryset = (
            CancellationReason.objects
            .filter(is_active=True)
            .order_by("type", "reason")
        )

        self.fields["reason"].empty_label = "Select cancellation reason"

    def clean_cancellation_charge(self):
        value = self.cleaned_data.get("cancellation_charge")

        if value is not None and value < 0:
            raise forms.ValidationError(
                "Cancellation charge cannot be negative."
            )

        return value


class RideRatingForm(forms.ModelForm):
    class Meta:
        model = RideRating
        fields = [
            "ride",
            "from_user",
            "to_user",
            "rating",
            "review",
        ]
        widgets = {
            "ride": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "from_user": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "to_user": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "rating": forms.Select(
                choices=[
                    (1, "1 Star"),
                    (2, "2 Stars"),
                    (3, "3 Stars"),
                    (4, "4 Stars"),
                    (5, "5 Stars"),
                ],
                attrs={
                    "class": "form-select",
                },
            ),
            "review": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter review",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["ride"].queryset = (
            Ride.objects
            .select_related(
                "passenger",
                "driver",
                "vehicle",
                "pickup_location",
                "drop_location",
            )
            .order_by("-created_at")
        )

        self.fields["from_user"].queryset = (
            self.fields["from_user"].queryset.order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        self.fields["to_user"].queryset = (
            self.fields["to_user"].queryset.order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        self.fields["ride"].empty_label = "Select ride"
        self.fields["from_user"].empty_label = "Select rating user"
        self.fields["to_user"].empty_label = "Select receiving user"

    def clean_rating(self):
        value = self.cleaned_data.get("rating")

        if value is None or not 1 <= value <= 5:
            raise forms.ValidationError(
                "Rating must be between 1 and 5."
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        ride = cleaned_data.get("ride")
        from_user = cleaned_data.get("from_user")
        to_user = cleaned_data.get("to_user")

        if from_user and to_user and from_user == to_user:
            self.add_error(
                "to_user",
                "A user cannot rate themselves.",
            )

        if ride and from_user and to_user:
            passenger = ride.passenger
            driver_user = getattr(ride.driver, "user", None)

            allowed_users = {
                user
                for user in [passenger, driver_user]
                if user is not None
            }

            if from_user not in allowed_users:
                self.add_error(
                    "from_user",
                    "Only the passenger or assigned driver can give a rating for this ride.",
                )

            if to_user not in allowed_users:
                self.add_error(
                    "to_user",
                    "The rating recipient must be the passenger or assigned driver of this ride.",
                )

            if (
                from_user
                and to_user
                and from_user == passenger
                and driver_user
                and to_user != driver_user
            ):
                self.add_error(
                    "to_user",
                    "A passenger rating should be given to the assigned driver.",
                )

            if (
                from_user
                and to_user
                and driver_user
                and from_user == driver_user
                and to_user != passenger
            ):
                self.add_error(
                    "to_user",
                    "A driver rating should be given to the passenger.",
                )

        return cleaned_data