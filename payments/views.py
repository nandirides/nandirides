import uuid
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from rides.forms import RideRequestForm
from rides.models import RideRequest
from locations.models import City, Location
from vehicles.models import VehicleType
from django.contrib.auth import get_user_model

from .forms import RefundForm
from .models import Payment, Refund


def _generate_payment_number():
    return (
        f"NRPAY"
        f"{timezone.now().strftime('%Y%m%d%H%M%S')}"
        f"{uuid.uuid4().hex[:6].upper()}"
    )


def _generate_transaction_id():
    return f"NRTXN{uuid.uuid4().hex.upper()}"


def _normalize_ride_request_data(data):
    """Normalize ride-request values before RideRequestForm validation.

    City values can arrive as either database IDs or city names such as
    "Haridwar". The RideRequest form expects a City relation, so convert
    names to primary keys before validation and payment confirmation.
    """
    normalized = data.copy()
    for field_name in ("pickup_city", "drop_city", "city_id"):
        value = normalized.get(field_name)
        if value in (None, ""):
            continue
        value = str(value).strip()
        city = None
        if value.isdigit():
            city = City.objects.filter(pk=int(value)).first()
        if city is None:
            city = (
                City.objects
                .filter(name__iexact=value)
                .order_by("state__country__name", "state__name", "name", "id")
                .first()
            )
        if city:
            normalized[field_name] = str(city.pk)
    User = get_user_model()
    for field_name in ("passenger", "user"):
        value = normalized.get(field_name)
        if value in (None, ""):
            continue
        value = str(value).strip()
        user = None
        if value.isdigit():
            user = User.objects.filter(pk=int(value)).first()
        if user is None:
            user = User.objects.filter(username__iexact=value).first()
        if user:
            normalized[field_name] = str(user.pk)
    value = normalized.get("vehicle_type")
    if value not in (None, ""):
        value = str(value).strip()
        vehicle_type = None
        if value.isdigit():
            vehicle_type = VehicleType.objects.filter(pk=int(value)).first()
        if vehicle_type is None:
            vehicle_type = VehicleType.objects.filter(name__iexact=value).first()
        if vehicle_type:
            normalized["vehicle_type"] = str(vehicle_type.pk)
    for field_name in ("pickup_location", "drop_location"):
        if normalized.get(field_name) in (None, ""):
            normalized[field_name] = ""
    return normalized


def _create_location_from_ride_request_data(data, prefix):
    address = str(
        data.get(f"{prefix}_address")
        or data.get(f"{prefix}_location_address")
        or ""
    ).strip()
    city_value = data.get(f"{prefix}_city") or data.get(f"{prefix}_city_name")
    latitude = data.get(f"{prefix}_latitude")
    longitude = (
        data.get(f"{prefix}_longitude")
        or data.get(f"{prefix}_lng")
        or data.get(f"{prefix}_lon")
    )
    city = None
    if city_value not in (None, ""):
        city_value = str(city_value).strip()
        if city_value.isdigit():
            city = City.objects.filter(pk=int(city_value)).first()
        if city is None:
            city = City.objects.filter(name__iexact=city_value).first()
    if not address:
        address = city.name if city else f"{prefix.title()} Location"
    try:
        latitude = Decimal(str(latitude)) if latitude not in (None, "") else Decimal("0")
        longitude = Decimal(str(longitude)) if longitude not in (None, "") else Decimal("0")
    except (TypeError, ValueError, ArithmeticError):
        return None
    return Location.objects.create(
        address=address,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )


def _payment_form_data(request):
    """
    Store only ride-request-related fields.

    Sensitive payment fields such as full card number,
    CVV, expiry, UPI ID and card name are excluded.
    """
    excluded_fields = {
        "csrfmiddlewaretoken",
        "payment_method",
        "card_number",
        "card_cvv",
        "card_expiry",
        "card_name",
        "upi_id",
        "netbanking_bank",
        "wallet_provider",
    }

    return {
        key: value
        for key, value in request.POST.items()
        if key not in excluded_fields
    }


def _payment_card_data(request):
    """
    Store only safe card information.

    Never store the complete card number or CVV.
    """
    card_number = request.POST.get("card_number", "").strip()
    card_name = request.POST.get("card_name", "").strip()
    card_expiry = request.POST.get("card_expiry", "").strip()

    card_last4 = ""

    if card_number:
        digits = "".join(
            character
            for character in card_number
            if character.isdigit()
        )

        if len(digits) >= 4:
            card_last4 = digits[-4:]

    return {
        "card_brand": "",
        "card_last4": card_last4,
        "card_name": card_name,
        "card_expiry": card_expiry,
    }


def payment_list(request):
    payments = (
        Payment.objects.select_related(
            "user",
            "ride",
            "ride_request",
        )
        .prefetch_related("refunds")
        .all()
        .order_by("-id")
    )

    context = {
        "payments": payments,
        "breadcrumb_items": [
            {
                "title": "Payments",
                "url": "payment_list",
            },
        ],
        "total_payments": payments.count(),
        "pending_payments": payments.filter(
            status=Payment.Status.PENDING
        ).count(),
        "successful_payments": payments.filter(
            status=Payment.Status.SUCCESS
        ).count(),
        "failed_payments": payments.filter(
            status=Payment.Status.FAILED
        ).count(),
        "refunded_payments": payments.filter(
            status=Payment.Status.REFUNDED
        ).count(),
    }

    return render(
        request,
        "payment/payment_list.html",
        context,
    )


def payment_detail(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related(
            "user",
            "ride",
            "ride_request",
        ).prefetch_related("refunds"),
        pk=pk,
    )

    refunds = payment.refunds.all().order_by("-id")

    context = {
        "payment": payment,
        "refunds": refunds,
        "page_title": "Payment Details",
        "breadcrumb_items": [
            {
                "title": "Payment Details",
                "url": "payment_detail",
            },
        ],
    }

    return render(
        request,
        "payment/payment_detail.html",
        context,
    )


@require_POST
def create_ride_payment(request):
    """
    Creates a pending payment.

    At this stage, RideRequest is not created yet.
    RideRequest is created during payment confirmation.
    """

    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login before making a payment.",
            },
            status=401,
        )

    payment_method = (
        request.POST.get("payment_method", "")
        .strip()
        .lower()
    )

    valid_methods = {
        Payment.Method.CARD,
        Payment.Method.UPI,
        Payment.Method.WALLET,
        Payment.Method.NETBANKING,
        Payment.Method.CASH,
    }

    if payment_method not in valid_methods:
        return JsonResponse(
            {
                "success": False,
                "message": "Please select a valid payment method.",
            },
            status=400,
        )

    ride_request_data = _normalize_ride_request_data(
        _payment_form_data(request)
    )
    validation_data = ride_request_data.copy()
    for field_name in ("pickup_city", "drop_city", "city_id", "passenger", "vehicle_type"):
        if field_name in ride_request_data:
            validation_data[field_name] = ride_request_data[field_name]
    validation_data["pickup_location"] = ""
    validation_data["drop_location"] = ""
    form = RideRequestForm(
        validation_data,
        request.FILES,
    )

    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "message": "Please correct the ride request details.",
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )

    amount = form.cleaned_data.get("estimated_fare")

    if amount is None:
        return JsonResponse(
            {
                "success": False,
                "message": "Fare could not be calculated.",
            },
            status=400,
        )

    amount = Decimal(amount).quantize(
        Decimal("0.01")
    )

    if amount <= Decimal("0.00"):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid payment amount.",
            },
            status=400,
        )

    payment_data = ride_request_data

    card_data = {}

    if payment_method == Payment.Method.CARD:
        card_data = _payment_card_data(request)

    gateway_order_id = (
        f"DEMOORDER{uuid.uuid4().hex.upper()}"
    )

    payment = Payment.objects.create(
        payment_number=_generate_payment_number(),
        user=request.user,
        amount=amount,
        payment_method=payment_method,
        gateway="demo",
        gateway_order_id=gateway_order_id,
        card_brand=card_data.get("card_brand", ""),
        card_last4=card_data.get("card_last4", ""),
        status=Payment.Status.PENDING,
        metadata={
            "ride_request_data": payment_data,
            "payment_method": payment_method,
            "card_name": card_data.get("card_name", ""),
            "card_expiry": card_data.get("card_expiry", ""),
            "created_from": "ride_request_form",
            "demo_payment": True,
        },
    )

    return JsonResponse(
        {
            "success": True,
            "payment_id": payment.pk,
            "payment_number": payment.payment_number,
            "gateway_order_id": payment.gateway_order_id,
            "amount": str(payment.amount),
            "payment_method": payment.payment_method,
            "status": payment.status,
            "message": "Payment initiated successfully.",
        }
    )


@require_POST
def confirm_ride_payment(request, pk):
    """
    Confirms a demo payment and creates the RideRequest.

    Digital demo payments:
        Payment status becomes SUCCESS.

    Cash payments:
        RideRequest is created, but payment remains PENDING.
        Cash is not automatically marked as successful.
    """

    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login before confirming payment.",
            },
            status=401,
        )

    with transaction.atomic():
        payment = get_object_or_404(
            Payment.objects.select_for_update(),
            pk=pk,
            user=request.user,
        )

        if payment.ride_request_id:
            return JsonResponse(
                {
                    "success": True,
                    "payment_id": payment.pk,
                    "payment_number": payment.payment_number,
                    "ride_request_id": payment.ride_request_id,
                    "transaction_id": payment.transaction_id,
                    "message": "Ride Request was already created.",
                    "redirect_url": reverse(
                        "ride_request_details",
                        kwargs={
                            "pk": payment.ride_request_id,
                        },
                    ),
                }
            )

        if payment.status != Payment.Status.PENDING:
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "This payment is already "
                        f"{payment.get_status_display().lower()}."
                    ),
                },
                status=400,
            )

        ride_request_data = payment.metadata.get(
            "ride_request_data",
            {},
        )

        if not isinstance(ride_request_data, dict):
            payment.status = Payment.Status.FAILED
            payment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            return JsonResponse(
                {
                    "success": False,
                    "message": "Ride request payment data is invalid.",
                },
                status=400,
            )

        ride_request_data = _normalize_ride_request_data(
            ride_request_data
        )

        passenger_value = ride_request_data.get("passenger")
        vehicle_type_value = ride_request_data.get("vehicle_type")
        request_number = str(
            ride_request_data.get("request_number") or ""
        ).strip()
        status = str(
            ride_request_data.get("status") or RideRequest.Status.REQUESTED
        ).strip()

        UserModel = get_user_model()
        passenger = None
        if passenger_value not in (None, ""):
            passenger = UserModel.objects.filter(pk=passenger_value).first()

        if passenger is None:
            payment.status = Payment.Status.FAILED
            payment.metadata = {
                **payment.metadata,
                "ride_request_validation_errors": {
                    "passenger": [{
                        "message": "Selected passenger is no longer available.",
                        "code": "invalid_choice",
                    }]
                },
            }
            payment.save(update_fields=["status", "metadata", "updated_at"])
            return JsonResponse({
                "success": False,
                "message": "Selected passenger is no longer available.",
            }, status=400)

        vehicle_type = None
        if vehicle_type_value not in (None, ""):
            vehicle_type = (
                ride_request_data.get("vehicle_type")
            )
            from vehicles.models import VehicleType
            vehicle_type = VehicleType.objects.filter(pk=vehicle_type).first()

        if vehicle_type is None:
            payment.status = Payment.Status.FAILED
            payment.metadata = {
                **payment.metadata,
                "ride_request_validation_errors": {
                    "vehicle_type": [{
                        "message": "Selected vehicle type is no longer available.",
                        "code": "invalid_choice",
                    }]
                },
            }
            payment.save(update_fields=["status", "metadata", "updated_at"])
            return JsonResponse({
                "success": False,
                "message": "Selected vehicle type is no longer available.",
            }, status=400)

        pickup_location = None
        drop_location = None
        pickup_location_value = ride_request_data.get("pickup_location")
        drop_location_value = ride_request_data.get("drop_location")

        if pickup_location_value not in (None, ""):
            pickup_location = Location.objects.filter(pk=pickup_location_value).first()
        if drop_location_value not in (None, ""):
            drop_location = Location.objects.filter(pk=drop_location_value).first()

        if not request_number:
            timestamp = timezone.localtime().strftime("%Y%m%d%H%M%S")
            request_number = f"REQ-{timestamp}-{uuid.uuid4().hex[:6].upper()}"

        if status not in dict(RideRequest.Status.choices):
            status = RideRequest.Status.REQUESTED

        scheduled_at = ride_request_data.get("scheduled_at") or None
        if scheduled_at:
            scheduled_at = parse_datetime(str(scheduled_at))
            if scheduled_at is not None and timezone.is_naive(scheduled_at):
                scheduled_at = timezone.make_aware(scheduled_at)
        distance = ride_request_data.get("estimated_distance") or None
        duration = ride_request_data.get("estimated_duration") or None

        try:
            distance = Decimal(str(distance)) if distance not in (None, "") else None
            duration = int(duration) if duration not in (None, "") else None
        except (TypeError, ValueError, ArithmeticError):
            payment.status = Payment.Status.FAILED
            payment.metadata = {
                **payment.metadata,
                "ride_request_validation_errors": {
                    "estimated_distance": [{
                        "message": "Invalid distance or duration.",
                        "code": "invalid",
                    }]
                },
            }
            payment.save(update_fields=["status", "metadata", "updated_at"])
            return JsonResponse({
                "success": False,
                "message": "Invalid ride distance or duration.",
            }, status=400)

        ride_request = RideRequest(
            request_number=request_number,
            passenger=passenger,
            pickup_location=pickup_location,
            drop_location=drop_location,
            vehicle_type=vehicle_type,
            scheduled_at=scheduled_at,
            estimated_distance=distance,
            estimated_duration=duration,
            estimated_fare=payment.amount,
            status=status,
        )

        ride_request.user = request.user

        if hasattr(ride_request, "status"):
            ride_request.status = "requested"

        ride_request.estimated_fare = payment.amount

        if not ride_request.pickup_location_id:
            pickup_location = _create_location_from_ride_request_data(
                ride_request_data,
                "pickup",
            )
            if pickup_location is None:
                payment.status = Payment.Status.FAILED
                payment.metadata = {
                    **payment.metadata,
                    "ride_request_validation_errors": {
                        "pickup_location": [
                            {
                                "message": "Pickup location could not be created.",
                                "code": "invalid_location",
                            }
                        ]
                    },
                }
                payment.save(
                    update_fields=["status", "metadata", "updated_at"]
                )
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Pickup location could not be created.",
                    },
                    status=400,
                )
            ride_request.pickup_location = pickup_location

        if not ride_request.drop_location_id:
            drop_location = _create_location_from_ride_request_data(
                ride_request_data,
                "drop",
            )
            if drop_location is None:
                payment.status = Payment.Status.FAILED
                payment.metadata = {
                    **payment.metadata,
                    "ride_request_validation_errors": {
                        "drop_location": [
                            {
                                "message": "Drop location could not be created.",
                                "code": "invalid_location",
                            }
                        ]
                    },
                }
                payment.save(
                    update_fields=["status", "metadata", "updated_at"]
                )
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Drop location could not be created.",
                    },
                    status=400,
                )
            ride_request.drop_location = drop_location

        ride_request.save()

        payment_method = payment.payment_method

        if payment_method == Payment.Method.CASH:
            payment.status = Payment.Status.PENDING
            payment.transaction_id = ""
            payment.paid_at = None

            payment.metadata = {
                **payment.metadata,
                "confirmed_at": timezone.now().isoformat(),
                "cash_payment": True,
                "cash_payment_note": (
                    "Ride Request created. "
                    "Cash payment is pending manual collection."
                ),
            }

            success_message = (
                "Ride Request created successfully. "
                "Cash payment is pending."
            )

        else:
            payment.status = Payment.Status.SUCCESS
            payment.transaction_id = _generate_transaction_id()
            payment.paid_at = timezone.now()

            payment.metadata = {
                **payment.metadata,
                "confirmed_at": timezone.now().isoformat(),
                "demo_payment": True,
            }

            success_message = (
                "Demo payment completed successfully and "
                "Ride Request was created."
            )

        payment.ride_request = ride_request

        payment.save(
            update_fields=[
                "status",
                "transaction_id",
                "paid_at",
                "metadata",
                "ride_request",
                "updated_at",
            ]
        )

    return JsonResponse(
        {
            "success": True,
            "payment_id": payment.pk,
            "payment_number": payment.payment_number,
            "transaction_id": payment.transaction_id,
            "ride_request_id": ride_request.pk,
            "payment_status": payment.status,
            "message": success_message,
            "redirect_url": reverse(
                "ride_request_details",
                kwargs={
                    "pk": ride_request.pk,
                },
            ),
        }
    )


@require_POST
def fail_ride_payment(request, pk):
    """
    Marks a pending demo payment as failed.
    """

    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login first.",
            },
            status=401,
        )

    with transaction.atomic():
        payment = get_object_or_404(
            Payment.objects.select_for_update(),
            pk=pk,
            user=request.user,
        )

        if payment.status != Payment.Status.PENDING:
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Only pending payments can be failed."
                    ),
                },
                status=400,
            )

        if payment.ride_request_id:
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "This payment is already linked "
                        "to a Ride Request."
                    ),
                },
                status=400,
            )

        payment.status = Payment.Status.FAILED

        payment.metadata = {
            **payment.metadata,
            "failed_at": timezone.now().isoformat(),
        }

        payment.save(
            update_fields=[
                "status",
                "metadata",
                "updated_at",
            ]
        )

    return JsonResponse(
        {
            "success": True,
            "message": "Payment marked as failed.",
        }
    )


def refund_form(request, payment_pk, pk=None):
    payment = get_object_or_404(
        Payment,
        pk=payment_pk,
    )

    refund = None

    if pk:
        refund = get_object_or_404(
            Refund,
            pk=pk,
            payment=payment,
        )

    if request.method == "POST":
        form = RefundForm(
            request.POST,
            instance=refund,
            payment=payment,
        )

        if form.is_valid():
            with transaction.atomic():
                refund = form.save(
                    commit=False
                )

                refund.payment = payment
                refund.save()

            if pk:
                messages.success(
                    request,
                    "Refund updated successfully.",
                )
            else:
                messages.success(
                    request,
                    "Refund created successfully.",
                )

            return redirect(
                "payment_detail",
                pk=payment.pk,
            )
    else:
        form = RefundForm(
            instance=refund,
            payment=payment,
        )

    context = {
        "form": form,
        "payment": payment,
        "refund": refund,
        "page_title": (
            "Edit Refund"
            if pk
            else "Add Refund"
        ),
        "breadcrumb_items": [
            {
                "title": "Refunds",
                "url": reverse(
                    "payment_list"
                ),
            },
            {
                "title": (
                    "Edit Refund"
                    if pk
                    else "Add Refund"
                ),
                "url": (
                    reverse(
                        "refund_edit",
                        kwargs={
                            "payment_pk": payment.pk,
                            "pk": pk,
                        },
                    )
                    if pk
                    else reverse(
                        "refund_create",
                        kwargs={
                            "payment_pk": payment.pk,
                        },
                    )
                ),
            },
        ],
    }

    return render(
        request,
        "payment/refund_form.html",
        context,
    )