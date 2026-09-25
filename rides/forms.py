import uuid
from decimal import Decimal
from django import forms
from django.db.models import Q
from django.utils import timezone
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
from locations.models import City, Location
from pricing.models import FareRule, SurgePricing
from vehicles.models import Vehicle


class RideRequestForm(forms.ModelForm):
    pickup_address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter pickup location manually",
                "autocomplete": "off",
            }
        ),
    )

    drop_address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter destination manually",
                "autocomplete": "off",
            }
        ),
    )

    pickup_latitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )

    pickup_longitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )

    drop_latitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )

    drop_longitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )

    pickup_city = forms.ModelChoiceField(
        queryset=City.objects.select_related(
            "state",
            "state__country",
        ).order_by(
            "state__country__name",
            "state__name",
            "name",
        ),
        required=False,
        widget=forms.HiddenInput(),
    )

    drop_city = forms.ModelChoiceField(
        queryset=City.objects.select_related(
            "state",
            "state__country",
        ).order_by(
            "state__country__name",
            "state__name",
            "name",
        ),
        required=False,
        widget=forms.HiddenInput(),
    )

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
                    "placeholder": "Auto-generated request number",
                    "readonly": True,
                }
            ),
            "passenger": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "pickup_location": forms.HiddenInput(),
            "drop_location": forms.HiddenInput(),
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
                    "readonly": True,
                }
            ),
            "estimated_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "0",
                    "readonly": True,
                }
            ),
            "estimated_fare": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                    "readonly": True,
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def _generate_request_number(self):
        while True:
            timestamp = timezone.localtime().strftime("%Y%m%d%H%M%S")
            suffix = uuid.uuid4().hex[:6].upper()
            request_number = f"REQ-{timestamp}-{suffix}"

            if not RideRequest.objects.filter(
                request_number=request_number
            ).exists():
                return request_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["pickup_location"].required = False
        self.fields["drop_location"].required = False

        if not self.instance.pk:
            current_request_number = (
                self.initial.get("request_number")
                or getattr(
                    self.instance,
                    "request_number",
                    "",
                )
            )

            if not current_request_number:
                self.initial["request_number"] = (
                    self._generate_request_number()
                )

            self.fields["request_number"].widget.attrs["readonly"] = True

        if self.instance.pk:
            pickup = self.instance.pickup_location
            drop = self.instance.drop_location

            if pickup:
                self.initial["pickup_address"] = pickup.address
                self.initial["pickup_latitude"] = pickup.latitude
                self.initial["pickup_longitude"] = pickup.longitude
                self.initial["pickup_city"] = pickup.city_id

            if drop:
                self.initial["drop_address"] = drop.address
                self.initial["drop_latitude"] = drop.latitude
                self.initial["drop_longitude"] = drop.longitude
                self.initial["drop_city"] = drop.city_id

        self.fields["passenger"].queryset = (
            self.fields["passenger"].queryset.order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        self.fields["pickup_location"].queryset = (
            Location.objects
            .select_related(
                "city",
                "city__state",
                "city__state__country",
            )
            .order_by("address")
        )

        self.fields["drop_location"].queryset = (
            Location.objects
            .select_related(
                "city",
                "city__state",
                "city__state__country",
            )
            .order_by("address")
        )

        self.fields["pickup_location"].empty_label = None
        self.fields["drop_location"].empty_label = None

    @staticmethod
    def _validate_coordinates(latitude, longitude, prefix):
        errors = {}

        if latitude is not None:
            if latitude < Decimal("-90") or latitude > Decimal("90"):
                errors[f"{prefix}_latitude"] = (
                    "Latitude must be between -90 and 90."
                )

        if longitude is not None:
            if longitude < Decimal("-180") or longitude > Decimal("180"):
                errors[f"{prefix}_longitude"] = (
                    "Longitude must be between -180 and 180."
                )

        if (latitude is None) != (longitude is None):
            errors[f"{prefix}_latitude"] = (
                f"{prefix.title()} latitude and longitude must be provided together."
            )

        return errors

    def _get_fare_rule(self, city, vehicle_type):
        if not city or not vehicle_type:
            return None

        now = timezone.now()

        return (
            FareRule.objects
            .filter(
                city=city,
                vehicle_type=vehicle_type,
                is_active=True,
                effective_from__lte=now,
            )
            .filter(
                Q(effective_to__isnull=True)
                | Q(effective_to__gte=now)
            )
            .order_by(
                "-effective_from",
                "-id",
            )
            .first()
        )

    def _get_surge_multiplier(self, city, vehicle_type):
        if not city or not vehicle_type:
            return Decimal("1")

        now = timezone.now()

        surge = (
            SurgePricing.objects
            .filter(
                city=city,
                vehicle_type=vehicle_type,
                is_active=True,
                start_time__lte=now,
                end_time__gte=now,
            )
            .order_by(
                "-start_time",
                "-id",
            )
            .first()
        )

        if not surge:
            return Decimal("1")

        multiplier = surge.multiplier or Decimal("1")

        if multiplier <= 0:
            return Decimal("1")

        return multiplier

    def _calculate_fare(
        self,
        city,
        vehicle_type,
        distance,
        duration,
    ):
        if (
            not city
            or not vehicle_type
            or distance is None
            or duration is None
        ):
            return None

        fare_rule = self._get_fare_rule(
            city=city,
            vehicle_type=vehicle_type,
        )

        if not fare_rule:
            return None

        base_fare = (
            fare_rule.base_fare
            or Decimal("0")
        )

        per_km_rate = (
            fare_rule.per_km_rate
            or Decimal("0")
        )

        per_minute_rate = (
            fare_rule.per_minute_rate
            or Decimal("0")
        )

        minimum_fare = (
            fare_rule.minimum_fare
            or Decimal("0")
        )

        distance_fare = (
            distance * per_km_rate
        )

        time_fare = (
            Decimal(duration)
            * per_minute_rate
        )

        calculated_fare = (
            base_fare
            + distance_fare
            + time_fare
        )

        calculated_fare = max(
            calculated_fare,
            minimum_fare,
        )

        surge_multiplier = (
            self._get_surge_multiplier(
                city=city,
                vehicle_type=vehicle_type,
            )
        )

        calculated_fare = (
            calculated_fare
            * surge_multiplier
        )

        return calculated_fare.quantize(
            Decimal("0.01")
        )

    def clean(self):
        cleaned_data = super().clean()

        pickup = cleaned_data.get(
            "pickup_location"
        )

        drop = cleaned_data.get(
            "drop_location"
        )

        pickup_address = (
            cleaned_data.get(
                "pickup_address"
            )
            or ""
        ).strip()

        drop_address = (
            cleaned_data.get(
                "drop_address"
            )
            or ""
        ).strip()

        pickup_latitude = cleaned_data.get(
            "pickup_latitude"
        )

        pickup_longitude = cleaned_data.get(
            "pickup_longitude"
        )

        drop_latitude = cleaned_data.get(
            "drop_latitude"
        )

        drop_longitude = cleaned_data.get(
            "drop_longitude"
        )

        pickup_city = cleaned_data.get(
            "pickup_city"
        )

        drop_city = cleaned_data.get(
            "drop_city"
        )

        vehicle_type = cleaned_data.get(
            "vehicle_type"
        )

        distance = cleaned_data.get(
            "estimated_distance"
        )

        duration = cleaned_data.get(
            "estimated_duration"
        )

        fare = cleaned_data.get(
            "estimated_fare"
        )

        pickup_coordinate_errors = (
            self._validate_coordinates(
                pickup_latitude,
                pickup_longitude,
                "pickup",
            )
        )

        for field_name, error_message in (
            pickup_coordinate_errors.items()
        ):
            self.add_error(
                field_name,
                error_message,
            )

        drop_coordinate_errors = (
            self._validate_coordinates(
                drop_latitude,
                drop_longitude,
                "drop",
            )
        )

        for field_name, error_message in (
            drop_coordinate_errors.items()
        ):
            self.add_error(
                field_name,
                error_message,
            )

        has_pickup_coordinates = (
            pickup_latitude is not None
            and pickup_longitude is not None
        )

        has_drop_coordinates = (
            drop_latitude is not None
            and drop_longitude is not None
        )

        pickup_available = (
            bool(pickup)
            or bool(pickup_address)
            or has_pickup_coordinates
        )

        drop_available = (
            bool(drop)
            or bool(drop_address)
            or has_drop_coordinates
        )

        if not pickup_available:
            self.add_error(
                "pickup_address",
                "Please enter a pickup location or use the map/current location.",
            )

        if not drop_available:
            self.add_error(
                "drop_address",
                "Please enter a destination or select it on the map.",
            )

        if pickup and drop and pickup == drop:
            self.add_error(
                "drop_address",
                "Pickup and drop location cannot be the same.",
            )

        if (
            has_pickup_coordinates
            and has_drop_coordinates
            and pickup_latitude == drop_latitude
            and pickup_longitude == drop_longitude
        ):
            self.add_error(
                "drop_address",
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

        selected_city = (
            pickup_city
            or drop_city
            or getattr(
                pickup,
                "city",
                None,
            )
            or getattr(
                drop,
                "city",
                None,
            )
        )

        if (
            selected_city
            and vehicle_type
            and distance is not None
            and duration is not None
        ):
            calculated_fare = (
                self._calculate_fare(
                    city=selected_city,
                    vehicle_type=vehicle_type,
                    distance=distance,
                    duration=duration,
                )
            )

            if calculated_fare is not None:
                cleaned_data["estimated_fare"] = (
                    calculated_fare
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
                    "placeholder": "Auto-generated ride number",
                    "readonly": True,
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
                    "disabled": True,
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
                    "disabled": True,
                }
            ),
            "drop_location": forms.Select(
                attrs={
                    "class": "form-select",
                    "disabled": True,
                }
            ),
            "scheduled_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                    "readonly": True,
                }
            ),
            "distance_km": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                    "readonly": True,
                }
            ),
            "duration_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "0",
                    "readonly": True,
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

        current_vehicle_id = (
            self.instance.vehicle_id
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
                Q(ride__isnull=True)
                | Q(pk=current_request_id)
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
            Location.objects
            .select_related(
                "city",
                "city__state",
                "city__state__country",
            )
            .order_by("address")
        )

        self.fields["drop_location"].queryset = (
            Location.objects
            .select_related(
                "city",
                "city__state",
                "city__state__country",
            )
            .order_by("address")
        )

        self.fields["ride_request"].empty_label = (
            "Select ride request"
        )

        self.fields["driver"].empty_label = (
            "Select driver"
        )

        self.fields["vehicle"].empty_label = (
            "Select vehicle"
        )

        self.fields["passenger"].empty_label = None
        self.fields["pickup_location"].empty_label = None
        self.fields["drop_location"].empty_label = None

        self.fields["vehicle"].label_from_instance = (
            lambda obj: (
                f"{obj.vehicle_number} — "
                f"{obj.vehicle_type.name}"
                if obj.vehicle_type
                else obj.vehicle_number
            )
        )

        self.fields["pickup_location"].label_from_instance = (
            lambda obj: (
                obj.address
                or f"Location #{obj.pk}"
            )
        )

        self.fields["drop_location"].label_from_instance = (
            lambda obj: (
                obj.address
                or f"Location #{obj.pk}"
            )
        )

        if not self.instance.pk:
            self.fields["ride_number"].initial = (
                self._generate_ride_number()
            )

        selected_request_id = None

        if self.is_bound:
            selected_request_id = self.data.get(
                "ride_request"
            )

        if not selected_request_id:
            initial = kwargs.get("initial") or {}
            selected_request_id = initial.get(
                "ride_request"
            )

        if not selected_request_id:
            selected_request_id = current_request_id

        if selected_request_id:
            selected_request = (
                RideRequest.objects
                .select_related(
                    "passenger",
                    "vehicle_type",
                    "pickup_location",
                    "drop_location",
                )
                .filter(pk=selected_request_id)
                .first()
            )

            if selected_request:
                self.initial["passenger"] = (
                    selected_request.passenger_id
                )

                self.initial["pickup_location"] = (
                    selected_request.pickup_location_id
                )

                self.initial["drop_location"] = (
                    selected_request.drop_location_id
                )

                self.initial["scheduled_at"] = (
                    selected_request.scheduled_at
                )

                self.initial["distance_km"] = (
                    selected_request.estimated_distance
                )

                self.initial["duration_minutes"] = (
                    selected_request.estimated_duration
                )

                if selected_request.vehicle_type_id:
                    vehicle_queryset = (
                        Vehicle.objects
                        .select_related(
                            "vehicle_type"
                        )
                        .filter(
                            vehicle_type_id=(
                                selected_request.vehicle_type_id
                            )
                        )
                        .order_by(
                            "vehicle_number"
                        )
                    )

                    if current_vehicle_id:
                        vehicle_queryset = (
                            Vehicle.objects
                            .select_related(
                                "vehicle_type"
                            )
                            .filter(
                                Q(
                                    vehicle_type_id=(
                                        selected_request.vehicle_type_id
                                    )
                                )
                                | Q(
                                    pk=current_vehicle_id
                                )
                            )
                            .order_by(
                                "vehicle_number"
                            )
                        )

                    self.fields["vehicle"].queryset = (
                        vehicle_queryset
                    )

                if self.instance.pk:
                    self.initial["vehicle"] = (
                        self.instance.vehicle_id
                    )

        self.fields["passenger"].required = False
        self.fields["vehicle"].required = False
        self.fields["pickup_location"].required = False
        self.fields["drop_location"].required = False
        self.fields["scheduled_at"].required = False
        self.fields["distance_km"].required = False
        self.fields["duration_minutes"].required = False

        self.fields["passenger"].widget.attrs["disabled"] = True
        self.fields["pickup_location"].widget.attrs["disabled"] = True
        self.fields["drop_location"].widget.attrs["disabled"] = True

        self.fields["scheduled_at"].widget.attrs["readonly"] = True
        self.fields["distance_km"].widget.attrs["readonly"] = True
        self.fields["duration_minutes"].widget.attrs["readonly"] = True

    def _generate_ride_number(self):
        last_ride = (
            Ride.objects
            .exclude(ride_number__isnull=True)
            .exclude(ride_number="")
            .order_by("-id")
            .first()
        )

        if not last_ride:
            return "NR0001"

        last_number = None

        try:
            ride_number = str(
                last_ride.ride_number
            ).strip()

            if ride_number.upper().startswith("NR"):
                last_number = int(
                    ride_number[2:]
                )
            else:
                last_number = int(
                    ride_number
                )

        except (ValueError, TypeError):
            last_number = None

        if last_number is None:
            return "NR0001"

        return f"NR{last_number + 1}"

    def clean(self):
        cleaned_data = super().clean()

        ride_request = cleaned_data.get(
            "ride_request"
        )

        if not ride_request:
            return cleaned_data

        cleaned_data["passenger"] = (
            ride_request.passenger
        )

        cleaned_data["pickup_location"] = (
            ride_request.pickup_location
        )

        cleaned_data["drop_location"] = (
            ride_request.drop_location
        )

        cleaned_data["scheduled_at"] = (
            ride_request.scheduled_at
        )

        cleaned_data["distance_km"] = (
            ride_request.estimated_distance
        )

        cleaned_data["duration_minutes"] = (
            ride_request.estimated_duration
        )

        pickup = ride_request.pickup_location
        drop = ride_request.drop_location

        if (
            pickup
            and drop
            and pickup == drop
        ):
            self.add_error(
                "ride_request",
                "Pickup and drop location cannot be the same.",
            )

        distance = (
            ride_request.estimated_distance
        )

        if (
            distance is not None
            and distance < 0
        ):
            self.add_error(
                "ride_request",
                "Ride request distance cannot be negative.",
            )

        duration = (
            ride_request.estimated_duration
        )

        if (
            duration is not None
            and duration < 0
        ):
            self.add_error(
                "ride_request",
                "Ride request duration cannot be negative.",
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

        self.fields["ride"].queryset = (
            Ride.objects
            .select_related(
                "passenger",
                "driver",
                "vehicle",
            )
            .order_by("-created_at")
        )

        self.fields["location"].queryset = (
            Location.objects
            .order_by("address")
        )

        self.fields["location"].label_from_instance = (
            lambda obj: str(obj)
        )

    def clean_stop_order(self):
        stop_order = self.cleaned_data.get(
            "stop_order"
        )

        if stop_order is not None and stop_order < 1:
            raise forms.ValidationError(
                "Stop order must be at least 1."
            )

        return stop_order

    def clean(self):
        cleaned_data = super().clean()

        arrival_time = cleaned_data.get(
            "arrival_time"
        )

        departure_time = cleaned_data.get(
            "departure_time"
        )

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

        self.fields["driver"].empty_label = (
            "Select driver"
        )

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        accepted_at = cleaned_data.get("accepted_at")
        rejected_at = cleaned_data.get("rejected_at")
        rejection_reason = cleaned_data.get(
            "rejection_reason"
        )

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
                cleaned_data.get(
                    "rejection_reason"
                )
                or ""
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

        self.fields["driver"].empty_label = (
            "Select driver"
        )

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")
        speed = cleaned_data.get("speed")
        heading = cleaned_data.get("heading")
        accuracy = cleaned_data.get("accuracy")

        if (
            latitude is not None
            and not -90 <= latitude <= 90
        ):
            self.add_error(
                "latitude",
                "Latitude must be between -90 and 90.",
            )

        if (
            longitude is not None
            and not -180 <= longitude <= 180
        ):
            self.add_error(
                "longitude",
                "Longitude must be between -180 and 180.",
            )

        if speed is not None and speed < 0:
            self.add_error(
                "speed",
                "Speed cannot be negative.",
            )

        if (
            heading is not None
            and not 0 <= heading <= 360
        ):
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

        charge_applicable = cleaned_data.get(
            "charge_applicable"
        )

        charge_amount = cleaned_data.get(
            "charge_amount"
        )

        if charge_applicable and (
            charge_amount is None
            or charge_amount <= 0
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

        self.fields["reason"].empty_label = (
            "Select cancellation reason"
        )

    def clean_cancellation_charge(self):
        value = self.cleaned_data.get(
            "cancellation_charge"
        )

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

        self.fields["ride"].empty_label = (
            "Select ride"
        )

        self.fields["from_user"].empty_label = (
            "Select rating user"
        )

        self.fields["to_user"].empty_label = (
            "Select receiving user"
        )

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
            driver_user = getattr(
                ride.driver,
                "user",
                None,
            )

            allowed_users = {
                user
                for user in [
                    passenger,
                    driver_user,
                ]
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