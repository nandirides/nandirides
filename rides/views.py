from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest, urlopen
import json
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    RideCancellationForm,
    RideDriverAssignmentForm,
    RideForm,
    RideRatingForm,
    RideRequestForm,
    RideStatusForm,
    RideStopForm,
    RideTrackingForm,
)
from .models import (
    Ride,
    RideCancellation,
    RideDriverAssignment,
    RideRating,
    RideRequest,
    RideStop,
    RideTracking,
)
from locations.models import Location

try:
    from locations.models import City
except (ImportError, ModuleNotFoundError):
    City = None

try:
    from payments.models import Payment, Refund
except (ImportError, ModuleNotFoundError):
    Payment = None
    Refund = None


RIDE_REQUEST_ACTIVE_STATUSES = [
    RideRequest.Status.REQUESTED,
    RideRequest.Status.SEARCHING,
    RideRequest.Status.ASSIGNED,
]

RIDE_ACTIVE_STATUSES = [
    Ride.Status.DRIVER_ASSIGNED,
    Ride.Status.DRIVER_ARRIVING,
    Ride.Status.DRIVER_ARRIVED,
    Ride.Status.STARTED,
]

RIDE_LIVE_STATUSES = [
    Ride.Status.DRIVER_ASSIGNED,
    Ride.Status.DRIVER_ARRIVING,
    Ride.Status.DRIVER_ARRIVED,
    Ride.Status.STARTED,
]

GEOCODING_URL = "https://nominatim.openstreetmap.org"
ROUTING_URL = "https://router.project-osrm.org"
GEOCODING_USER_AGENT = "NandiRide/1.0 Django Ride Management"
GEOCODING_TIMEOUT = 8
ROUTING_TIMEOUT = 8


def _paginate(request, queryset, default_per_page=15):
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page

    per_page = max(5, min(per_page, 100))

    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def _ride_request_queryset():
    return (
        RideRequest.objects
        .select_related(
            "passenger",
            "pickup_location",
            "drop_location",
            "vehicle_type",
        )
        .order_by("-requested_at", "-pk")
    )


def _ride_queryset():
    return (
        Ride.objects
        .select_related(
            "ride_request",
            "passenger",
            "driver",
            "vehicle",
            "pickup_location",
            "drop_location",
        )
        .order_by("-created_at", "-pk")
    )


def _model_text_fields(model):
    fields = []

    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue

        if getattr(field, "many_to_many", False):
            continue

        if getattr(field, "one_to_many", False):
            continue

        if field.get_internal_type() in {
            "CharField",
            "TextField",
            "EmailField",
            "SlugField",
        }:
            fields.append(field.name)

    return fields


def _related_text_search(q_objects, relation_name, related_model, query):
    for field_name in _model_text_fields(related_model):
        q_objects.append(
            Q(
                **{
                    f"{relation_name}__{field_name}__icontains": query
                }
            )
        )


def _user_search(q_objects, relation_name, user_model, query):
    _related_text_search(
        q_objects,
        relation_name,
        user_model,
        query,
    )


def _driver_search(q_objects, query):
    try:
        driver_field = Ride._meta.get_field("driver")
        driver_model = driver_field.remote_field.model
    except Exception:
        return

    _related_text_search(
        q_objects,
        "driver",
        driver_model,
        query,
    )

    try:
        user_field = driver_model._meta.get_field("user")
        user_model = user_field.remote_field.model
    except Exception:
        return

    _user_search(
        q_objects,
        "driver__user",
        user_model,
        query,
    )


def _location_search(q_objects, relation_name, model, query):
    try:
        location_field = model._meta.get_field(relation_name)
        location_model = location_field.remote_field.model
    except Exception:
        return

    _related_text_search(
        q_objects,
        relation_name,
        location_model,
        query,
    )


def _combine_search_queries(q_objects):
    if not q_objects:
        return None

    combined = q_objects[0]

    for query in q_objects[1:]:
        combined |= query

    return combined


def _ride_search_filter(queryset, query):
    if not query:
        return queryset

    q_objects = [
        Q(ride_number__icontains=query),
        Q(passenger__username__icontains=query),
        Q(passenger__first_name__icontains=query),
        Q(passenger__last_name__icontains=query),
    ]

    try:
        passenger_field = Ride._meta.get_field("passenger")
        passenger_model = passenger_field.remote_field.model

        _user_search(
            q_objects,
            "passenger",
            passenger_model,
            query,
        )
    except Exception:
        pass

    _driver_search(q_objects, query)

    _location_search(
        q_objects,
        "pickup_location",
        Ride,
        query,
    )

    _location_search(
        q_objects,
        "drop_location",
        Ride,
        query,
    )

    combined_query = _combine_search_queries(q_objects)

    return (
        queryset.filter(combined_query).distinct()
        if combined_query is not None
        else queryset.none()
    )


def _request_search_filter(queryset, query):
    if not query:
        return queryset

    q_objects = [
        Q(request_number__icontains=query),
        Q(passenger__username__icontains=query),
        Q(passenger__first_name__icontains=query),
        Q(passenger__last_name__icontains=query),
    ]

    try:
        passenger_field = RideRequest._meta.get_field("passenger")
        passenger_model = passenger_field.remote_field.model

        _user_search(
            q_objects,
            "passenger",
            passenger_model,
            query,
        )
    except Exception:
        pass

    _location_search(
        q_objects,
        "pickup_location",
        RideRequest,
        query,
    )

    _location_search(
        q_objects,
        "drop_location",
        RideRequest,
        query,
    )

    combined_query = _combine_search_queries(q_objects)

    return (
        queryset.filter(combined_query).distinct()
        if combined_query is not None
        else queryset.none()
    )


def _safe_decimal(value):
    if value in (None, ""):
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _http_json(url, params=None, headers=None, timeout=8):
    try:
        if params:
            url = f"{url}?{urlencode(params)}"

        request = UrlRequest(
            url,
            headers=headers or {},
            method="GET",
        )

        with urlopen(request, timeout=timeout) as response:
            content = response.read().decode("utf-8")

        return json.loads(content)
    except Exception:
        return None


def _geocode_address(address):
    address = (address or "").strip()

    if not address:
        return None

    result = _http_json(
        f"{GEOCODING_URL}/search",
        params={
            "q": address,
            "format": "jsonv2",
            "limit": 1,
            "addressdetails": 1,
        },
        headers={
            "User-Agent": GEOCODING_USER_AGENT,
            "Accept-Language": "en",
        },
        timeout=GEOCODING_TIMEOUT,
    )

    if not result or not isinstance(result, list):
        return None

    item = result[0] if result else None

    if not item:
        return None

    latitude = _safe_decimal(item.get("lat"))
    longitude = _safe_decimal(item.get("lon"))

    if latitude is None or longitude is None:
        return None

    return {
        "latitude": latitude,
        "longitude": longitude,
        "display_name": (
            item.get("display_name")
            or address
        ),
        "address": item.get("address") or {},
    }


def _reverse_geocode(latitude, longitude):
    latitude = _safe_decimal(latitude)
    longitude = _safe_decimal(longitude)

    if latitude is None or longitude is None:
        return None

    result = _http_json(
        f"{GEOCODING_URL}/reverse",
        params={
            "lat": str(latitude),
            "lon": str(longitude),
            "format": "jsonv2",
            "zoom": 18,
            "addressdetails": 1,
        },
        headers={
            "User-Agent": GEOCODING_USER_AGENT,
            "Accept-Language": "en",
        },
        timeout=GEOCODING_TIMEOUT,
    )

    if not result:
        return None

    return {
        "latitude": latitude,
        "longitude": longitude,
        "display_name": result.get("display_name") or "",
        "address": result.get("address") or {},
    }


def _get_geocoder_city_name(geocoder_result):
    if not geocoder_result:
        return ""

    address = geocoder_result.get("address") or {}

    city_name = (
        address.get("city")
        or address.get("town")
        or address.get("municipality")
        or address.get("village")
        or address.get("suburb")
        or address.get("city_district")
        or ""
    )

    return str(city_name).strip()


def _resolve_city(city_name):
    if not City or not city_name:
        return None

    city_name = str(city_name).strip()

    if not city_name:
        return None

    city = (
        City.objects
        .filter(name__iexact=city_name)
        .order_by("pk")
        .first()
    )

    if city:
        return city

    return (
        City.objects
        .filter(name__icontains=city_name)
        .order_by("pk")
        .first()
    )


def _resolve_form_location_data(cleaned_data, prefix):
    address = (
        cleaned_data.get(f"{prefix}_address")
        or ""
    ).strip()

    latitude = _safe_decimal(
        cleaned_data.get(f"{prefix}_latitude")
    )

    longitude = _safe_decimal(
        cleaned_data.get(f"{prefix}_longitude")
    )

    existing_location = cleaned_data.get(
        f"{prefix}_location"
    )

    city = cleaned_data.get(
        f"{prefix}_city"
    )

    geocoder_result = None

    if latitude is None or longitude is None:
        if address:
            geocoder_result = _geocode_address(address)

            if geocoder_result:
                latitude = geocoder_result["latitude"]
                longitude = geocoder_result["longitude"]

    elif not address:
        geocoder_result = _reverse_geocode(
            latitude,
            longitude,
        )

        if geocoder_result:
            address = (
                geocoder_result.get("display_name")
                or address
            )

    if geocoder_result:
        display_name = (
            geocoder_result.get("display_name")
            or ""
        ).strip()

        if display_name and not address:
            address = display_name

        if not city:
            city = _resolve_city(
                _get_geocoder_city_name(
                    geocoder_result
                )
            )

    if not city and existing_location:
        city = getattr(
            existing_location,
            "city",
            None,
        )

    return {
        "existing_location": existing_location,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "city": city,
    }


def _get_or_create_form_location(
    cleaned_data,
    prefix,
    resolved_data=None,
):
    data = (
        resolved_data
        or _resolve_form_location_data(
            cleaned_data,
            prefix,
        )
    )

    address = (
        data.get("address")
        or "Selected Location"
    ).strip()

    latitude = _safe_decimal(
        data.get("latitude")
    )

    longitude = _safe_decimal(
        data.get("longitude")
    )

    city = data.get("city")

    existing_location = data.get(
        "existing_location"
    )

    if latitude is None or longitude is None:
        return None

    if existing_location:
        same_coordinates = (
            _safe_decimal(
                existing_location.latitude
            ) == latitude
            and _safe_decimal(
                existing_location.longitude
            ) == longitude
        )

        same_address = (
            existing_location.address == address
        )

        same_city = (
            existing_location.city_id
            == getattr(city, "pk", None)
        )

        if (
            same_coordinates
            and same_address
            and same_city
        ):
            return existing_location

    location = (
        Location.objects
        .filter(
            latitude=latitude,
            longitude=longitude,
            address=address,
        )
        .first()
    )

    if location:
        if (
            city
            and location.city_id != city.pk
        ):
            location.city = city
            location.save(
                update_fields=["city"]
            )

        return location

    return Location.objects.create(
        address=address,
        latitude=latitude,
        longitude=longitude,
        city=city,
    )


def _get_route_details(
    pickup_latitude,
    pickup_longitude,
    drop_latitude,
    drop_longitude,
):
    pickup_latitude = _safe_decimal(
        pickup_latitude
    )
    pickup_longitude = _safe_decimal(
        pickup_longitude
    )
    drop_latitude = _safe_decimal(
        drop_latitude
    )
    drop_longitude = _safe_decimal(
        drop_longitude
    )

    if any(
        value is None
        for value in [
            pickup_latitude,
            pickup_longitude,
            drop_latitude,
            drop_longitude,
        ]
    ):
        return None

    if (
        pickup_latitude == drop_latitude
        and pickup_longitude == drop_longitude
    ):
        return None

    coordinate_string = (
        f"{pickup_longitude},{pickup_latitude};"
        f"{drop_longitude},{drop_latitude}"
    )

    result = _http_json(
        f"{ROUTING_URL}/route/v1/driving/{coordinate_string}",
        params={
            "overview": "false",
            "steps": "false",
            "alternatives": "false",
        },
        headers={
            "User-Agent": GEOCODING_USER_AGENT,
        },
        timeout=ROUTING_TIMEOUT,
    )

    if not result:
        return None

    if result.get("code") != "Ok":
        return None

    routes = result.get("routes") or []

    if not routes:
        return None

    route = routes[0]

    distance_meters = _safe_decimal(
        route.get("distance")
    )

    duration_seconds = _safe_decimal(
        route.get("duration")
    )

    if (
        distance_meters is None
        or duration_seconds is None
    ):
        return None

    distance_km = (
        distance_meters / Decimal("1000")
    ).quantize(
        Decimal("0.01")
    )

    duration_minutes = max(
        1,
        int(
            (
                duration_seconds
                / Decimal("60")
            ).quantize(
                Decimal("1")
            )
        ),
    )

    return {
        "distance": distance_km,
        "duration": duration_minutes,
    }


def _update_form_location_fields(
    form,
    prefix,
    location_data,
):
    if not location_data:
        return

    address = location_data.get("address")
    latitude = location_data.get("latitude")
    longitude = location_data.get("longitude")
    city = location_data.get("city")

    if address:
        form.cleaned_data[
            f"{prefix}_address"
        ] = address

    if latitude is not None:
        form.cleaned_data[
            f"{prefix}_latitude"
        ] = latitude

    if longitude is not None:
        form.cleaned_data[
            f"{prefix}_longitude"
        ] = longitude

    if city:
        form.cleaned_data[
            f"{prefix}_city"
        ] = city


def _calculate_request_fare(
    form,
    city,
    distance,
    duration,
):
    vehicle_type = form.cleaned_data.get(
        "vehicle_type"
    )

    if not all(
        [
            city,
            vehicle_type,
            distance is not None,
            duration is not None,
        ]
    ):
        return None

    try:
        return form._calculate_fare(
            city=city,
            vehicle_type=vehicle_type,
            distance=distance,
            duration=duration,
        )
    except TypeError:
        try:
            return form._calculate_fare(
                vehicle_type,
                city,
                distance,
                duration,
            )
        except Exception:
            return None
    except Exception:
        return None


def _allowed_next_statuses(ride):
    transitions = {
        Ride.Status.DRIVER_ASSIGNED: [
            Ride.Status.DRIVER_ARRIVING,
            Ride.Status.CANCELLED,
        ],
        Ride.Status.DRIVER_ARRIVING: [
            Ride.Status.DRIVER_ARRIVED,
            Ride.Status.CANCELLED,
        ],
        Ride.Status.DRIVER_ARRIVED: [
            Ride.Status.STARTED,
            Ride.Status.CANCELLED,
        ],
        Ride.Status.STARTED: [
            Ride.Status.COMPLETED,
            Ride.Status.CANCELLED,
        ],
        Ride.Status.COMPLETED: [],
        Ride.Status.CANCELLED: [],
    }

    return transitions.get(
        ride.status,
        [],
    )


def _payment_for_ride(ride):
    if Payment is None:
        return None

    try:
        payment_field_names = {
            field.name
            for field in Payment._meta.get_fields()
        }

        if "ride" in payment_field_names:
            payment = (
                Payment.objects
                .filter(ride=ride)
                .order_by("-pk")
                .first()
            )

            if payment:
                return payment

        if "ride_request" in payment_field_names:
            ride_request = getattr(
                ride,
                "ride_request",
                None,
            )

            if ride_request:
                return (
                    Payment.objects
                    .filter(
                        ride_request=ride_request
                    )
                    .order_by("-pk")
                    .first()
                )
    except Exception:
        return None

    return None


def _refund_payment_for_cancelled_request(
    ride_request,
    ride=None,
):
    """
    Automatically create a full local refund for a successful payment.

    This is intentionally a demo/local refund flow:
    - no external payment gateway is called
    - Refund DB record is created
    - Payment status becomes refunded
    - duplicate refund records are prevented
    """

    if (
        Payment is None
        or Refund is None
        or ride_request is None
    ):
        return None

    payment = None

    try:
        payment_field_names = {
            field.name
            for field in Payment._meta.get_fields()
        }

        # First preference: payment directly linked to RideRequest.
        if "ride_request" in payment_field_names:
            payment = (
                Payment.objects
                .filter(
                    ride_request=ride_request
                )
                .order_by("-pk")
                .first()
            )

        # Fallback: payment linked to the Ride.
        if (
            payment is None
            and ride is not None
            and "ride" in payment_field_names
        ):
            payment = (
                Payment.objects
                .filter(
                    ride=ride
                )
                .order_by("-pk")
                .first()
            )

    except Exception:
        return None

    if not payment:
        return None

    try:
        # Prevent duplicate refunds.
        existing_refund = (
            Refund.objects
            .filter(
                payment=payment
            )
            .order_by("-pk")
            .first()
        )

        if existing_refund:
            payment_status = str(
                getattr(
                    payment,
                    "status",
                    "",
                )
            ).lower()

            if payment_status != "refunded":
                payment.status = "refunded"
                payment.save(
                    update_fields=["status"]
                )

            return existing_refund

        # Only successful payments are refundable.
        payment_status = str(
            getattr(
                payment,
                "status",
                "",
            )
        ).lower()

        if payment_status != "success":
            return None

        refund_amount = _safe_decimal(
            getattr(
                payment,
                "amount",
                None,
            )
        )

        if (
            refund_amount is None
            or refund_amount <= 0
        ):
            return None

        now = timezone.now()

        payment_number = getattr(
            payment,
            "payment_number",
            str(payment.pk),
        )

        refund = Refund.objects.create(
            payment=payment,
            refund_amount=refund_amount,
            reason=(
                "Automatic full refund generated because "
                f"ride request {ride_request.request_number} "
                "was cancelled."
            ),
            refund_reference=(
                f"RF-{payment_number}-"
                f"{uuid.uuid4().hex[:12].upper()}"
            ),
            status="processed",
            processed_at=now,
        )

        payment.status = "refunded"

        payment.save(
            update_fields=["status"]
        )

        return refund

    except Exception:
        return None


def _sync_request_status_from_ride(ride):
    try:
        ride_request = ride.ride_request
    except RideRequest.DoesNotExist:
        return

    mapping = {
        Ride.Status.DRIVER_ASSIGNED: RideRequest.Status.ASSIGNED,
        Ride.Status.DRIVER_ARRIVING: RideRequest.Status.ACCEPTED,
        Ride.Status.DRIVER_ARRIVED: RideRequest.Status.ACCEPTED,
        Ride.Status.STARTED: RideRequest.Status.ACCEPTED,
        Ride.Status.COMPLETED: RideRequest.Status.COMPLETED,
        Ride.Status.CANCELLED: RideRequest.Status.CANCELLED,
    }

    new_status = mapping.get(
        ride.status
    )

    if (
        new_status
        and ride_request.status != new_status
    ):
        ride_request.status = new_status
        ride_request.save(
            update_fields=["status"]
        )

    if ride.status == Ride.Status.CANCELLED:
        _refund_payment_for_cancelled_request(
            ride_request,
            ride=ride,
        )


@login_required
def ride_request_list(request):
    queryset = _ride_request_queryset()

    query = request.GET.get(
        "q",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    queryset = _request_search_filter(
        queryset,
        query,
    )

    if status:
        queryset = queryset.filter(
            status=status
        )

    page_obj = _paginate(
        request,
        queryset,
    )

    context = {
        "page_title": "Ride Requests",
        "breadcrumb_items": [
            {
                "title": "Ride Requests",
                "url": "ride_request_list",
            },
        ],
        "ride_requests": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": query,
        "selected_status": status,
        "total_requests": RideRequest.objects.count(),
        "requested_count": RideRequest.objects.filter(
            status=RideRequest.Status.REQUESTED
        ).count(),
        "searching_count": RideRequest.objects.filter(
            status=RideRequest.Status.SEARCHING
        ).count(),
        "assigned_count": RideRequest.objects.filter(
            status=RideRequest.Status.ASSIGNED
        ).count(),
        "status_choices": RideRequest.Status.choices,
    }

    return render(
        request,
        "rides/ride_request_list.html",
        context,
    )


@login_required
def ride_request_fare_preview(request):
    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method.",
            },
            status=405,
        )

    vehicle_type_id = request.GET.get(
        "vehicle_type",
        "",
    ).strip()

    city_name = request.GET.get(
        "city_name",
        "",
    ).strip()

    city_id = request.GET.get(
        "city_id",
        "",
    ).strip()

    distance = _safe_decimal(
        request.GET.get("distance")
    )

    duration = request.GET.get(
        "duration",
        "",
    ).strip()

    try:
        duration_value = (
            int(duration)
            if duration
            else None
        )
    except (TypeError, ValueError):
        duration_value = None

    if (
        not vehicle_type_id
        or distance is None
        or duration_value is None
    ):
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Vehicle, city, distance and duration "
                    "are required."
                ),
            },
            status=400,
        )

    city = None

    if city_id and City:
        try:
            city = (
                City.objects
                .filter(pk=city_id)
                .first()
            )
        except (TypeError, ValueError):
            city = None

    if not city and city_name:
        city = _resolve_city(
            city_name
        )

    if not city:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Pricing city could not be identified "
                    "for this location."
                ),
            },
            status=404,
        )

    form = RideRequestForm()

    vehicle_type = (
        form.fields["vehicle_type"]
        .queryset
        .filter(pk=vehicle_type_id)
        .first()
    )

    if not vehicle_type:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Selected vehicle type is invalid."
                ),
            },
            status=400,
        )

    fare = form._calculate_fare(
        city=city,
        vehicle_type=vehicle_type,
        distance=distance,
        duration=duration_value,
    )

    if fare is None:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "No active fare rule is configured "
                    "for this vehicle and location."
                ),
            },
            status=404,
        )

    return JsonResponse(
        {
            "success": True,
            "fare": str(fare),
            "city": city.name,
            "vehicle_type": str(vehicle_type),
        }
    )


@login_required
@transaction.atomic
def ride_request_create_edit(request, pk=None):
    if (
        request.method == "GET"
        and request.GET.get("fare_preview") == "1"
    ):
        return ride_request_fare_preview(request)

    ride_request = (
        get_object_or_404(
            RideRequest,
            pk=pk,
        )
        if pk
        else None
    )

    if request.method == "POST":
        form = RideRequestForm(
            request.POST,
            instance=ride_request,
        )

        if form.is_valid():
            cleaned_data = form.cleaned_data

            pickup_data = _resolve_form_location_data(
                cleaned_data,
                "pickup",
            )

            drop_data = _resolve_form_location_data(
                cleaned_data,
                "drop",
            )

            pickup_location = None
            drop_location = None

            pickup_latitude = pickup_data.get(
                "latitude"
            )

            pickup_longitude = pickup_data.get(
                "longitude"
            )

            drop_latitude = drop_data.get(
                "latitude"
            )

            drop_longitude = drop_data.get(
                "longitude"
            )

            if (
                pickup_latitude is None
                or pickup_longitude is None
            ):
                form.add_error(
                    "pickup_address",
                    (
                        "Pickup location could not be found. "
                        "Please enter a more specific address "
                        "or select the pickup point on the map."
                    ),
                )

            if (
                drop_latitude is None
                or drop_longitude is None
            ):
                form.add_error(
                    "drop_address",
                    (
                        "Destination could not be found. "
                        "Please enter a more specific address "
                        "or select the destination on the map."
                    ),
                )

            if not form.errors:
                pickup_location = (
                    _get_or_create_form_location(
                        cleaned_data,
                        "pickup",
                        pickup_data,
                    )
                )

                drop_location = (
                    _get_or_create_form_location(
                        cleaned_data,
                        "drop",
                        drop_data,
                    )
                )

            if (
                not form.errors
                and (
                    pickup_location is None
                    or drop_location is None
                )
            ):
                form.add_error(
                    None,
                    (
                        "Pickup and destination locations "
                        "could not be determined."
                    ),
                )

            if (
                not form.errors
                and pickup_location.pk
                == drop_location.pk
            ):
                form.add_error(
                    None,
                    (
                        "Pickup and drop locations "
                        "must be different."
                    ),
                )

            route = None

            if not form.errors:
                route = _get_route_details(
                    pickup_latitude,
                    pickup_longitude,
                    drop_latitude,
                    drop_longitude,
                )

                if route:
                    cleaned_data[
                        "estimated_distance"
                    ] = route["distance"]

                    cleaned_data[
                        "estimated_duration"
                    ] = route["duration"]

                else:
                    existing_distance = _safe_decimal(
                        cleaned_data.get(
                            "estimated_distance"
                        )
                    )

                    existing_duration = cleaned_data.get(
                        "estimated_duration"
                    )

                    if (
                        existing_distance is None
                        or existing_duration is None
                    ):
                        form.add_error(
                            None,
                            (
                                "Route could not be calculated. "
                                "Please select valid pickup and "
                                "destination locations again."
                            ),
                        )

            if not form.errors:
                pickup_city = (
                    pickup_data.get("city")
                    or getattr(
                        pickup_location,
                        "city",
                        None,
                    )
                )

                drop_city = (
                    drop_data.get("city")
                    or getattr(
                        drop_location,
                        "city",
                        None,
                    )
                )

                city = pickup_city or drop_city

                if pickup_city:
                    cleaned_data[
                        "pickup_city"
                    ] = pickup_city

                if drop_city:
                    cleaned_data[
                        "drop_city"
                    ] = drop_city

                distance = _safe_decimal(
                    cleaned_data.get(
                        "estimated_distance"
                    )
                )

                duration = cleaned_data.get(
                    "estimated_duration"
                )

                calculated_fare = (
                    _calculate_request_fare(
                        form,
                        city,
                        distance,
                        duration,
                    )
                )

                if calculated_fare is not None:
                    cleaned_data[
                        "estimated_fare"
                    ] = calculated_fare

            if not form.errors:
                saved_request = form.save(
                    commit=False
                )

                saved_request.pickup_location = (
                    pickup_location
                )

                saved_request.drop_location = (
                    drop_location
                )

                distance = _safe_decimal(
                    cleaned_data.get(
                        "estimated_distance"
                    )
                )

                duration = cleaned_data.get(
                    "estimated_duration"
                )

                fare = _safe_decimal(
                    cleaned_data.get(
                        "estimated_fare"
                    )
                )

                if distance is not None:
                    saved_request.estimated_distance = (
                        distance
                    )

                if duration is not None:
                    saved_request.estimated_duration = (
                        duration
                    )

                if fare is not None:
                    saved_request.estimated_fare = (
                        fare
                    )

                saved_request.save()

                # -------------------------------------------------
                # AUTOMATIC REFUND FOR CANCELLED RIDE REQUEST
                # -------------------------------------------------
                refund = None

                if (
                    saved_request.status
                    == RideRequest.Status.CANCELLED
                ):
                    linked_ride = (
                        Ride.objects
                        .filter(
                            ride_request=saved_request
                        )
                        .order_by("-pk")
                        .first()
                    )

                    refund = (
                        _refund_payment_for_cancelled_request(
                            saved_request,
                            ride=linked_ride,
                        )
                    )

                if refund:
                    messages.success(
                        request,
                        (
                            f"Ride request "
                            f"{saved_request.request_number} "
                            f"has been updated successfully. "
                            f"₹{refund.refund_amount} refund "
                            f"has been processed automatically."
                        ),
                    )
                else:
                    messages.success(
                        request,
                        (
                            f"Ride request "
                            f"{saved_request.request_number} "
                            f"has been "
                            f"{'updated' if ride_request else 'created'} "
                            f"successfully."
                        ),
                    )

                return redirect(
                    "ride_request_details",
                    pk=saved_request.pk,
                )

    else:
        form = RideRequestForm(
            instance=ride_request
        )

    context = {
        "page_title": (
            "Edit Ride Request"
            if ride_request
            else "Create Ride Request"
        ),
        "breadcrumb_items": [
            {
                "title": (
                    "Edit Ride Request"
                    if ride_request
                    else "Create Ride Request"
                ),
                "url": (
                    reverse(
                        "ride_request_edit",
                        args=[ride_request.id],
                    )
                    if ride_request
                    else reverse(
                        "ride_request_add"
                    )
                ),
            },
        ],
        "form": form,
        "ride_request": ride_request,
        "is_edit": bool(ride_request),
    }

    return render(
        request,
        "rides/ride_request_form.html",
        context,
    )


@login_required
def ride_request_details(request, pk):
    ride_request = get_object_or_404(
        _ride_request_queryset(),
        pk=pk,
    )

    ride = (
        Ride.objects
        .filter(
            ride_request=ride_request
        )
        .select_related(
            "passenger",
            "driver",
            "vehicle",
            "pickup_location",
            "drop_location",
        )
        .first()
    )

    payment = None
    refund = None
    refunds = []

    if Payment is not None:
        try:
            payment = (
                Payment.objects
                .filter(
                    ride_request=ride_request
                )
                .order_by("-pk")
                .first()
            )

            if payment and Refund is not None:
                refunds = list(
                    Refund.objects
                    .filter(
                        payment=payment
                    )
                    .order_by(
                        "-requested_at",
                        "-pk",
                    )
                )

                refund = (
                    refunds[0]
                    if refunds
                    else None
                )
        except Exception:
            payment = None
            refund = None
            refunds = []

    context = {
        "breadcrumb_items": [
            {
                "title": "Ride Request",
                "url": "ride_request_list",
            },
        ],
        "ride_request": ride_request,
        "ride": ride,
        "linked_ride": ride,
        "payment": payment,
        "refund": refund,
        "refund_details": refund,
        "refunds": refunds,
    }

    return render(
        request,
        "rides/ride_request_details.html",
        context,
    )


@login_required
def ride_request_delete(request, pk):
    ride_request = get_object_or_404(
        RideRequest,
        pk=pk,
    )

    if request.method != "POST":
        return redirect(
            "ride_request_details",
            pk=ride_request.pk,
        )

    if Ride.objects.filter(
        ride_request=ride_request
    ).exists():
        messages.error(
            request,
            (
                "This ride request cannot be deleted "
                "because a ride is linked to it."
            ),
        )

        return redirect(
            "ride_request_details",
            pk=ride_request.pk,
        )

    request_number = ride_request.request_number

    ride_request.delete()

    messages.success(
        request,
        f"Ride request {request_number} has been deleted.",
    )

    return redirect(
        "ride_request_list"
    )


@login_required
@transaction.atomic
def ride_request_status_update(request, pk):
    ride_request = get_object_or_404(
        RideRequest,
        pk=pk,
    )

    if request.method != "POST":
        return redirect(
            "ride_request_details",
            pk=ride_request.pk,
        )

    new_status = request.POST.get(
        "status",
        "",
    ).strip()

    valid_statuses = {
        value
        for value, label in RideRequest.Status.choices
    }

    if new_status not in valid_statuses:
        messages.error(
            request,
            "Invalid ride request status.",
        )

        return redirect(
            "ride_request_details",
            pk=ride_request.pk,
        )

    old_status = ride_request.status

    ride_request.status = new_status

    ride_request.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    # -------------------------------------------------
    # AUTOMATIC REFUND WHEN STATUS IS CANCELLED
    # -------------------------------------------------
    refund = None

    if (
        new_status == RideRequest.Status.CANCELLED
        and old_status != RideRequest.Status.CANCELLED
    ):
        linked_ride = (
            Ride.objects
            .filter(
                ride_request=ride_request
            )
            .order_by("-pk")
            .first()
        )

        refund = _refund_payment_for_cancelled_request(
            ride_request,
            ride=linked_ride,
        )

    if refund:
        messages.success(
            request,
            (
                f"Ride request "
                f"{ride_request.request_number} "
                f"status updated to "
                f"{ride_request.get_status_display()}. "
                f"₹{refund.refund_amount} refund "
                f"has been processed automatically."
            ),
        )
    else:
        messages.success(
            request,
            (
                f"Ride request "
                f"{ride_request.request_number} status updated to "
                f"{ride_request.get_status_display()}."
            ),
        )

    return redirect(
        "ride_request_details",
        pk=ride_request.pk,
    )


@login_required
def ride_list(request):
    queryset = _ride_queryset()

    query = request.GET.get(
        "q",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    queryset = _ride_search_filter(
        queryset,
        query,
    )

    if status:
        queryset = queryset.filter(
            status=status
        )

    page_obj = _paginate(
        request,
        queryset,
    )

    context = {
        #"page_title": "Rides",
        "breadcrumb_items": [
            {
                "title": "Rides",
                "url": "ride_list",
            },
        ],
        "rides": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": query,
        "selected_status": status,
        "total_rides": Ride.objects.count(),
        "active_rides": Ride.objects.filter(
            status__in=RIDE_ACTIVE_STATUSES
        ).count(),
        "completed_rides": Ride.objects.filter(
            status=Ride.Status.COMPLETED
        ).count(),
        "cancelled_rides": Ride.objects.filter(
            status=Ride.Status.CANCELLED
        ).count(),
        "status_choices": Ride.Status.choices,
    }

    return render(
        request,
        "rides/ride_list.html",
        context,
    )


@login_required
@transaction.atomic
def ride_create_edit(request, pk=None):
    ride = (
        get_object_or_404(
            _ride_queryset(),
            pk=pk,
        )
        if pk
        else None
    )

    request_pk = (
        request.POST.get("ride_request")
        or request.GET.get("ride_request")
    )

    source_request = None

    if request_pk:
        source_request = (
            RideRequest.objects
            .filter(pk=request_pk)
            .select_related(
                "passenger",
                "pickup_location",
                "drop_location",
                "vehicle_type",
            )
            .first()
        )

    if request.method == "POST":
        form = RideForm(
            request.POST,
            instance=ride,
        )

        if form.is_valid():
            selected_request = form.cleaned_data.get(
                "ride_request"
            )

            selected_vehicle = form.cleaned_data.get(
                "vehicle"
            )

            if not selected_request:
                form.add_error(
                    "ride_request",
                    "Please select a ride request.",
                )

            if not selected_vehicle:
                form.add_error(
                    "vehicle",
                    "Please select a vehicle.",
                )

            if (
                selected_request
                and selected_vehicle
                and selected_request.vehicle_type_id
                and selected_vehicle.vehicle_type_id
                != selected_request.vehicle_type_id
            ):
                form.add_error(
                    "vehicle",
                    (
                        "Selected vehicle does not match "
                        "the vehicle type of the ride request."
                    ),
                )

            if not form.errors:
                source_request = (
                    RideRequest.objects
                    .filter(pk=selected_request.pk)
                    .select_related(
                        "passenger",
                        "pickup_location",
                        "drop_location",
                        "vehicle_type",
                    )
                    .first()
                )

                if not source_request:
                    form.add_error(
                        "ride_request",
                        (
                            "Selected ride request "
                            "could not be found."
                        ),
                    )

            if not form.errors and source_request:
                saved_ride = form.save(
                    commit=False
                )

                saved_ride.ride_request = (
                    source_request
                )

                saved_ride.passenger = (
                    source_request.passenger
                )

                saved_ride.vehicle = (
                    selected_vehicle
                )

                saved_ride.pickup_location = (
                    source_request.pickup_location
                )

                saved_ride.drop_location = (
                    source_request.drop_location
                )

                saved_ride.scheduled_at = (
                    source_request.scheduled_at
                )

                saved_ride.distance_km = (
                    source_request.estimated_distance
                )

                saved_ride.duration_minutes = (
                    source_request.estimated_duration
                )

                if not saved_ride.ride_number:
                    saved_ride.ride_number = (
                        form._generate_ride_number()
                    )

                saved_ride.save()

                form.save_m2m()

                _sync_request_status_from_ride(
                    saved_ride
                )

                messages.success(
                    request,
                    (
                        f"Ride {saved_ride.ride_number} "
                        f"has been "
                        f"{'updated' if ride else 'created'} "
                        f"successfully."
                    ),
                )

                return redirect(
                    "ride_details",
                    pk=saved_ride.pk,
                )
    else:
        initial = {}

        selected_request = (
            source_request
            or (
                ride.ride_request
                if ride
                else None
            )
        )

        if selected_request:
            initial = {
                "ride_request": selected_request.pk,
                "passenger": selected_request.passenger_id,
                "pickup_location": selected_request.pickup_location_id,
                "drop_location": selected_request.drop_location_id,
                "scheduled_at": selected_request.scheduled_at,
                "distance_km": selected_request.estimated_distance,
                "duration_minutes": selected_request.estimated_duration,
            }

            if ride and ride.vehicle_id:
                initial["vehicle"] = (
                    ride.vehicle_id
                )

        form = RideForm(
            instance=ride,
            initial=initial,
        )

    context = {
        "breadcrumb_items": [
            {
                "title": (
                    "Edit Ride"
                    if ride
                    else "Create Ride"
                ),
                "url": (
                    reverse(
                        "ride_edit",
                        args=[ride.id],
                    )
                    if ride
                    else reverse("ride_add")
                ),
            },
        ],
        "form": form,
        "ride": ride,
        "object": ride,
        "ride_request": (
            source_request
            or (
                ride.ride_request
                if ride
                else None
            )
        ),
        "is_edit": bool(ride),
    }

    return render(
        request,
        "rides/ride_form.html",
        context,
    )


@login_required
def ride_status_update(request, pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=pk,
    )

    if request.method == "POST":
        form = RideStatusForm(
            request.POST,
            instance=ride,
        )

        if form.is_valid():
            new_status = form.cleaned_data.get(
                "status"
            )

            if new_status == ride.status:
                messages.info(
                    request,
                    "Ride is already in this status.",
                )

                return redirect(
                    "ride_details",
                    pk=ride.pk,
                )

            allowed = _allowed_next_statuses(
                ride
            )

            if (
                allowed
                and new_status not in allowed
            ):
                messages.error(
                    request,
                    (
                        "This status transition is not allowed "
                        "from the current ride status."
                    ),
                )
            else:
                old_status = ride.status
                ride.status = new_status
                now = timezone.now()

                if new_status == Ride.Status.DRIVER_ARRIVED:
                    ride.arrived_at = now
                elif new_status == Ride.Status.STARTED:
                    ride.started_at = (
                        ride.started_at
                        or now
                    )
                elif new_status == Ride.Status.COMPLETED:
                    ride.completed_at = now

                ride.save()

                _sync_request_status_from_ride(
                    ride
                )

                messages.success(
                    request,
                    (
                        f"Ride {ride.ride_number} changed from "
                        f"{dict(Ride.Status.choices).get(old_status, old_status)} "
                        f"to {ride.get_status_display()}."
                    ),
                )

                return redirect(
                    "ride_details",
                    pk=ride.pk,
                )
    else:
        form = RideStatusForm(
            instance=ride
        )

    context = {
        "page_title": f"Update Status - {ride.ride_number}",
        "breadcrumb_items": [
            {
                "title": "Update Status",
                "url": "ride_status_update",
            },
        ],
        "form": form,
        "ride": ride,
        "ride_request": ride.ride_request,
        "allowed_next_statuses": _allowed_next_statuses(
            ride
        ),
    }

    return render(
        request,
        "rides/ride_status_form.html",
        context,
    )


@login_required
def ride_delete(request, pk):
    ride = get_object_or_404(
        Ride,
        pk=pk,
    )

    if request.method != "POST":
        return redirect(
            "ride_details",
            pk=ride.pk,
        )

    ride_number = ride.ride_number

    ride.delete()

    messages.success(
        request,
        f"Ride {ride_number} has been deleted.",
    )

    return redirect(
        "ride_list"
    )


@login_required
def ride_details(request, pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=pk,
    )

    assignments = (
        ride.driver_assignments
        .select_related("driver")
        .order_by("-assigned_at")
    )

    stops = (
        ride.stops
        .select_related("location")
        .order_by("stop_order")
    )

    tracking_points = (
        ride.tracking_points
        .select_related("driver")
        .order_by("-recorded_at")
    )

    latest_tracking = tracking_points.first()

    ratings = (
        ride.ratings
        .select_related(
            "from_user",
            "to_user",
        )
        .order_by("-created_at")
    )

    cancellation = (
        RideCancellation.objects
        .filter(ride=ride)
        .select_related(
            "cancelled_by",
            "reason",
        )
        .first()
    )

    payment = _payment_for_ride(
        ride
    )

    refunds = []

    refund = None

    if payment and Refund is not None:
        try:
            refunds = list(
                Refund.objects
                .filter(
                    payment=payment
                )
                .order_by(
                    "-requested_at",
                    "-pk",
                )
            )

            refund = (
                refunds[0]
                if refunds
                else None
            )
        except Exception:
            refunds = []
            refund = None

    context = {
        "page_title": f"Ride {ride.ride_number}",
        "breadcrumb_items": [
            {
                "title": "Ride",
                "url": "ride_details",
            },
        ],
        "ride": ride,
        "ride_request": ride.ride_request,
        "assignments": assignments,
        "stops": stops,
        "tracking_points": tracking_points[:50],
        "latest_tracking": latest_tracking,
        "ratings": ratings,
        "cancellation": cancellation,
        "payment": payment,
        "refund": refund,
        "refund_details": refund,
        "refunds": refunds,
        "allowed_next_statuses": _allowed_next_statuses(
            ride
        ),
    }

    return render(
        request,
        "rides/ride_details.html",
        context,
    )


@login_required
def ride_assignment_list(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )

    assignments = (
        ride.driver_assignments
        .select_related("driver")
        .order_by("-assigned_at")
    )

    context = {
        "page_title": (
            f"Driver Assignments - "
            f"{ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Driver Assignment",
                "url": "ride_assignment_list",
            },
        ],
        "ride": ride,
        "assignments": assignments,
        "total_assignments": assignments.count(),
    }

    return render(
        request,
        "rides/assignment_list.html",
        context,
    )


@login_required
@transaction.atomic
def ride_assignment_create(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )

    if request.method == "POST":
        form = RideDriverAssignmentForm(
            request.POST
        )

        if form.is_valid():
            assignment = form.save(
                commit=False
            )

            assignment.ride = ride
            assignment.save()

            if (
                ride.status
                == Ride.Status.DRIVER_ASSIGNED
                and assignment.status
                == RideDriverAssignment.Status.ACCEPTED
            ):
                ride.status = Ride.Status.DRIVER_ARRIVING

                ride.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                _sync_request_status_from_ride(
                    ride
                )

            elif ride.status not in RIDE_LIVE_STATUSES:
                ride.status = Ride.Status.DRIVER_ASSIGNED

                ride.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                _sync_request_status_from_ride(
                    ride
                )

            messages.success(
                request,
                "Driver assignment created successfully.",
            )

            return redirect(
                "ride_assignment_list",
                ride_pk=ride.pk,
            )
    else:
        form = RideDriverAssignmentForm()

    context = {
        "page_title": (
            f"Assign Driver - "
            f"{ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Assign Driver",
                "url": "ride_assignment_add",
            },
        ],
        "form": form,
        "ride": ride,
        "assignment": None,
    }

    return render(
        request,
        "rides/assignment_form.html",
        context,
    )


@login_required
def ride_assignment_edit(request, pk):
    assignment = get_object_or_404(
        RideDriverAssignment.objects.select_related(
            "ride",
            "ride__passenger",
            "ride__vehicle",
            "driver",
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = RideDriverAssignmentForm(
            request.POST,
            instance=assignment,
        )

        if form.is_valid():
            updated_assignment = form.save()

            messages.success(
                request,
                "Driver assignment updated successfully.",
            )

            return redirect(
                "ride_assignment_list",
                ride_pk=updated_assignment.ride.pk,
            )
    else:
        form = RideDriverAssignmentForm(
            instance=assignment
        )

    context = {
        "page_title": (
            f"Edit Assignment - "
            f"{assignment.ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Edit Assignment",
                "url": "ride_assignment_edit",
            },
        ],
        "form": form,
        "ride": assignment.ride,
        "assignment": assignment,
    }

    return render(
        request,
        "rides/assignment_form.html",
        context,
    )


@login_required
def ride_assignment_delete(request, pk):
    assignment = get_object_or_404(
        RideDriverAssignment.objects.select_related(
            "ride"
        ),
        pk=pk,
    )

    ride_pk = assignment.ride.pk

    if request.method != "POST":
        return redirect(
            "ride_assignment_list",
            ride_pk=ride_pk,
        )

    assignment.delete()

    messages.success(
        request,
        "Driver assignment deleted successfully.",
    )

    return redirect(
        "ride_assignment_list",
        ride_pk=ride_pk,
    )


@login_required
def ride_tracking_list(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )

    queryset = (
        ride.tracking_points
        .select_related("driver")
        .order_by("-recorded_at")
    )

    page_obj = _paginate(
        request,
        queryset,
        default_per_page=20,
    )

    context = {
        "page_title": (
            f"Tracking - "
            f"{ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Tracking",
                "url": "ride_tracking_list",
            },
        ],
        "ride": ride,
        "tracking_points": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "latest_tracking": queryset.first(),
        "tracking_count": queryset.count(),
    }

    return render(
        request,
        "rides/ride_tracking_list.html",
        context,
    )


@login_required
def ride_tracking_create(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )

    if request.method == "POST":
        form = RideTrackingForm(
            request.POST
        )

        if form.is_valid():
            tracking = form.save(
                commit=False
            )

            tracking.ride = ride

            if (
                not tracking.driver_id
                and ride.driver_id
            ):
                tracking.driver_id = ride.driver_id

            tracking.save()

            messages.success(
                request,
                "Ride tracking point added successfully.",
            )

            return redirect(
                "ride_tracking_list",
                ride_pk=ride.pk,
            )
    else:
        initial = {}

        if ride.driver_id:
            initial["driver"] = ride.driver_id

        form = RideTrackingForm(
            initial=initial
        )

    context = {
        "breadcrumb_items": [
            {
                "title": "Add Tracking Point",
                "url": "ride_tracking_add",
            },
        ],
        "form": form,
        "ride": ride,
        "tracking": None,
    }

    return render(
        request,
        "rides/ride_tracking_form.html",
        context,
    )


@login_required
def ride_tracking_delete(request, pk):
    tracking = get_object_or_404(
        RideTracking.objects.select_related(
            "ride"
        ),
        pk=pk,
    )

    ride_pk = tracking.ride.pk

    if request.method != "POST":
        return redirect(
            "ride_tracking_list",
            ride_pk=ride_pk,
        )

    tracking.delete()

    messages.success(
        request,
        "Ride tracking point deleted successfully.",
    )

    return redirect(
        "ride_tracking_list",
        ride_pk=ride_pk,
    )


@login_required
@transaction.atomic
def ride_cancellation_create(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )
    if ride.status == Ride.Status.CANCELLED:
        messages.info(
            request,
            "This ride has already been cancelled.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if ride.status == Ride.Status.COMPLETED:
        messages.error(
            request,
            "A completed ride cannot be cancelled.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    existing_cancellation = (
        RideCancellation.objects
        .filter(ride=ride)
        .first()
    )
    if existing_cancellation:
        messages.info(
            request,
            "This ride already has a cancellation record.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["ride"] = str(ride.pk)
        post_data["cancelled_by"] = str(request.user.pk)
        form = RideCancellationForm(
            post_data
        )
        if form.is_valid():
            cancellation = form.save(
                commit=False
            )
            cancellation.ride = ride
            cancellation.cancelled_by = request.user
            cancellation.save()
            ride.status = Ride.Status.CANCELLED
            ride.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )
            _sync_request_status_from_ride(
                ride
            )
            refund = None
            if (
                Payment is not None
                and Refund is not None
            ):
                payment = _payment_for_ride(
                    ride
                )
                if payment:
                    try:
                        refund = (
                            Refund.objects
                            .filter(
                                payment=payment,
                                status__in=[
                                    "processed",
                                    "completed",
                                    "success",
                                ],
                            )
                            .order_by("-pk")
                            .first()
                        )
                    except Exception:
                        refund = None
            if refund:
                messages.success(
                    request,
                    (
                        f"Ride {ride.ride_number} has been "
                        f"cancelled successfully. "
                        f"₹{refund.refund_amount} refund "
                        f"has been processed."
                    ),
                )
            else:
                messages.success(
                    request,
                    (
                        f"Ride {ride.ride_number} has been "
                        f"cancelled successfully."
                    ),
                )
            return redirect(
                "ride_details",
                pk=ride.pk,
            )
    else:
        form = RideCancellationForm(
            initial={
                "ride": ride.pk,
                "cancelled_by": request.user.pk,
            }
        )
    context = {
        "page_title": (
            f"Cancel Ride - "
            f"{ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Cancel Ride",
                "url": "ride_cancellation_add",
            },
        ],
        "form": form,
        "ride": ride,
    }
    return render(
        request,
        "rides/ride_cancellation_form.html",
        context,
    )


@login_required
def ride_rating_create(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )
    passenger = ride.passenger
    driver_user = None
    if ride.driver_id:
        try:
            driver_user = ride.driver.user
        except AttributeError:
            driver_user = None
    if not passenger:
        messages.error(
            request,
            "This ride does not have a passenger.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if not driver_user:
        messages.error(
            request,
            "This ride does not have an assigned driver.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["ride"] = str(ride.pk)
        post_data["from_user"] = str(passenger.pk)
        post_data["to_user"] = str(driver_user.pk)
        form = RideRatingForm(
            post_data
        )
        if form.is_valid():
            rating = form.save(
                commit=False
            )
            rating.ride = ride
            rating.from_user = passenger
            rating.to_user = driver_user
            rating.save()
            messages.success(
                request,
                "Ride rating has been added successfully.",
            )
            return redirect(
                "ride_details",
                pk=ride.pk,
            )
    else:
        form = RideRatingForm(
            initial={
                "ride": ride.pk,
                "from_user": passenger.pk,
                "to_user": driver_user.pk,
            }
        )
    context = {
        "page_title": (
            f"Rate Ride - "
            f"{ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Rate Ride",
                "url": "ride_rating_add",
            },
        ],
        "form": form,
        "ride": ride,
    }
    return render(
        request,
        "rides/ride_rating_form.html",
        context,
    )

@login_required
def ride_stop_list(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )

    stops = (
        ride.stops
        .select_related("location")
        .order_by("stop_order")
    )

    context = {
        "page_title": (
            f"Ride Stops - "
            f"{ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Ride Stops",
                "url": "ride_stop_list",
            },
        ],
        "ride": ride,
        "stops": stops,
        "total_stops": stops.count(),
    }

    return render(
        request,
        "rides/ride_stop_list.html",
        context,
    )


@login_required
def ride_stop_create(request, ride_pk):
    ride = get_object_or_404(
        _ride_queryset(),
        pk=ride_pk,
    )

    if request.method == "POST":
        form = RideStopForm(
            request.POST
        )

        if form.is_valid():
            stop = form.save(
                commit=False
            )

            stop.ride = ride
            stop.save()

            messages.success(
                request,
                "Ride stop added successfully.",
            )

            return redirect(
                "ride_stop_list",
                ride_pk=ride.pk,
            )
    else:
        next_order = ride.stops.count() + 1

        form = RideStopForm(
            initial={
                "stop_order": next_order
            }
        )

    context = {
        "page_title": (
            f"Add Stop - "
            f"{ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Add Stop",
                "url": "ride_stop_add",
            },
        ],
        "form": form,
        "ride": ride,
        "stop": None,
    }

    return render(
        request,
        "rides/ride_stop_form.html",
        context,
    )


@login_required
def ride_stop_edit(request, pk):
    stop = get_object_or_404(
        RideStop.objects.select_related(
            "ride",
            "ride__passenger",
            "location",
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = RideStopForm(
            request.POST,
            instance=stop,
        )

        if form.is_valid():
            updated_stop = form.save()

            messages.success(
                request,
                "Ride stop updated successfully.",
            )

            return redirect(
                "ride_stop_list",
                ride_pk=updated_stop.ride.pk,
            )
    else:
        form = RideStopForm(
            instance=stop
        )

    context = {
        "page_title": (
            f"Edit Stop - "
            f"{stop.ride.ride_number}"
        ),
        "breadcrumb_items": [
            {
                "title": "Edit Stop",
                "url": "ride_stop_edit",
            },
        ],
        "form": form,
        "ride": stop.ride,
        "stop": stop,
    }

    return render(
        request,
        "rides/ride_stop_form.html",
        context,
    )


@login_required
def ride_stop_delete(request, pk):
    stop = get_object_or_404(
        RideStop.objects.select_related(
            "ride"
        ),
        pk=pk,
    )

    ride_pk = stop.ride.pk

    if request.method != "POST":
        return redirect(
            "ride_stop_list",
            ride_pk=ride_pk,
        )

    stop.delete()

    messages.success(
        request,
        "Ride stop deleted successfully.",
    )

    return redirect(
        "ride_stop_list",
        ride_pk=ride_pk,
    )


@login_required
def ride_dashboard(request):
    request_status_counts = {
        status: RideRequest.objects.filter(
            status=status
        ).count()
        for status in [
            RideRequest.Status.REQUESTED,
            RideRequest.Status.SEARCHING,
            RideRequest.Status.ASSIGNED,
            RideRequest.Status.ACCEPTED,
            RideRequest.Status.CANCELLED,
            RideRequest.Status.EXPIRED,
            RideRequest.Status.COMPLETED,
        ]
    }

    ride_status_counts = {
        status: Ride.objects.filter(
            status=status
        ).count()
        for status in [
            Ride.Status.DRIVER_ASSIGNED,
            Ride.Status.DRIVER_ARRIVING,
            Ride.Status.DRIVER_ARRIVED,
            Ride.Status.STARTED,
            Ride.Status.COMPLETED,
            Ride.Status.CANCELLED,
        ]
    }

    context = {
        "page_title": "Ride Dashboard",
        "breadcrumb_items": [
            {
                "title": "Ride Dashboard",
                "url": "ride_dashboard",
            },
        ],
        "total_requests": RideRequest.objects.count(),
        "requested_requests": request_status_counts[
            RideRequest.Status.REQUESTED
        ],
        "searching_requests": request_status_counts[
            RideRequest.Status.SEARCHING
        ],
        "assigned_requests": request_status_counts[
            RideRequest.Status.ASSIGNED
        ],
        "accepted_requests": request_status_counts[
            RideRequest.Status.ACCEPTED
        ],
        "cancelled_requests": request_status_counts[
            RideRequest.Status.CANCELLED
        ],
        "expired_requests": request_status_counts[
            RideRequest.Status.EXPIRED
        ],
        "completed_requests": request_status_counts[
            RideRequest.Status.COMPLETED
        ],
        "total_rides": Ride.objects.count(),
        "active_rides": Ride.objects.filter(
            status__in=RIDE_ACTIVE_STATUSES
        ).count(),
        "driver_assigned_rides": ride_status_counts[
            Ride.Status.DRIVER_ASSIGNED
        ],
        "driver_arriving_rides": ride_status_counts[
            Ride.Status.DRIVER_ARRIVING
        ],
        "driver_arrived_rides": ride_status_counts[
            Ride.Status.DRIVER_ARRIVED
        ],
        "started_rides": ride_status_counts[
            Ride.Status.STARTED
        ],
        "completed_rides": ride_status_counts[
            Ride.Status.COMPLETED
        ],
        "cancelled_rides": ride_status_counts[
            Ride.Status.CANCELLED
        ],
        "recent_rides": _ride_queryset()[:10],
        "recent_requests": _ride_request_queryset()[:10],
    }

    return render(
        request,
        "rides/ride_dashboard.html",
        context,
    )