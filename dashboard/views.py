from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
import re
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.db import transaction
from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from .forms import GalleryForm, UserCreateForm
from .models import AccountNotificationPreference, AccountPaymentDetail, Gallery, UserAddress, UserProfile, WalletTransaction
from drivers.models import Driver
from locations.models import City, Country, Location, State
from payments.models import Payment, Refund
from pricing.models import FareBreakdown, FareRule, SurgePricing
from promotions.models import Coupon, CouponUsage
from rides.models import Ride, RideRequest
from support.models import SupportTicket
from vehicles.models import Vehicle, VehicleType
from django.core.exceptions import PermissionDenied
from .models import GroupStatus


EMAIL_VERIFICATION_SALT = "nandiride-email-verification"
EMAIL_VERIFICATION_MAX_AGE = 86400


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _json_error(message, status=400):
    return JsonResponse(
        {
            "success": False,
            "message": message,
        },
        status=status,
    )


def _json_success(message="", **kwargs):
    data = {
        "success": True,
        "message": message,
    }
    data.update(kwargs)
    return JsonResponse(data)


def _field_names(model):
    return {
        field.name
        for field in model._meta.get_fields()
    }


def _safe_count(model, filters=None):
    filters = filters or {}
    fields = _field_names(model)
    if not all(
        key.split("__")[0] in fields
        for key in filters
    ):
        return model.objects.count()
    return model.objects.filter(**filters).count()


def _safe_sum(model, field_names):
    fields = _field_names(model)
    for field_name in field_names:
        if field_name in fields:
            result = model.objects.aggregate(
                total=Sum(field_name)
            )
            return result["total"] or Decimal("0")
    return Decimal("0")


def _safe_active_count(model):
    fields = _field_names(model)
    if "is_active" in fields:
        return model.objects.filter(
            is_active=True
        ).count()
    if "status" in fields:
        active_values = [
            "active",
            "Active",
            "ACTIVE",
        ]
        return model.objects.filter(
            status__in=active_values
        ).count()
    return model.objects.count()


def _safe_status_count(model, values):
    fields = _field_names(model)
    if "status" not in fields:
        return 0
    return model.objects.filter(
        status__in=values
    ).count()


def _safe_verified_count(model):
    fields = _field_names(model)
    if "is_verified" in fields:
        return model.objects.filter(
            is_verified=True
        ).count()
    if "verified" in fields:
        return model.objects.filter(
            verified=True
        ).count()
    if "verification_status" in fields:
        return model.objects.filter(
            verification_status__in=[
                "verified",
                "approved",
                "active",
                "Verified",
                "Approved",
                "Active",
            ]
        ).count()
    return 0


def _safe_pending_verification_count(model):
    fields = _field_names(model)
    if "is_verified" in fields:
        return model.objects.filter(
            is_verified=False
        ).count()
    if "verified" in fields:
        return model.objects.filter(
            verified=False
        ).count()
    if "verification_status" in fields:
        return model.objects.filter(
            verification_status__in=[
                "pending",
                "submitted",
                "under_review",
                "Pending",
                "Submitted",
                "Under Review",
            ]
        ).count()
    return 0


@login_required
def ride_gallery(request):
    gallery = Gallery.objects.all().order_by("-date")
    if request.method == "POST":
        form = GalleryForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Gallery image added successfully.",
            )
            return redirect("ride_gallery")
    else:
        form = GalleryForm()
    return render(
        request,
        "includes/gallery.html",
        {
            "gallery": gallery,
            "galleries": gallery,
            "form": form,
        },
    )


@login_required
@transaction.atomic
def user_create(request, pk=None):
    user_obj = (
        get_object_or_404(User, pk=pk)
        if pk is not None
        else None
    )
    if request.method == "POST":
        action = request.POST.get(
            "action",
            "",
        )
        if action == "toggle_status":
            if user_obj is None:
                messages.error(
                    request,
                    "Invalid user.",
                )
                return redirect("user_list")
            if user_obj.pk == request.user.pk:
                messages.error(
                    request,
                    "You cannot change your own account status.",
                )
                return redirect("user_list")
            user_obj.is_active = not user_obj.is_active
            user_obj.save(
                update_fields=[
                    "is_active",
                ]
            )
            messages.success(
                request,
                "User status updated successfully.",
            )
            return redirect("user_list")
        form = UserCreateForm(
            request.POST,
            request.FILES,
            instance=user_obj,
        )
        if form.is_valid():
            saved_user = form.save()
            profile, _ = UserProfile.objects.get_or_create(
                user=saved_user
            )
            profile.phone = request.POST.get(
                "phone",
                profile.phone,
            ).strip()
            profile.gender = request.POST.get(
                "gender",
                profile.gender,
            ).strip()
            profile.address = request.POST.get(
                "address",
                profile.address,
            ).strip()
            profile.emergency_contact_name = request.POST.get(
                "emergency_contact_name",
                profile.emergency_contact_name,
            ).strip()
            profile.emergency_contact_phone = request.POST.get(
                "emergency_contact_phone",
                profile.emergency_contact_phone,
            ).strip()
            date_of_birth = request.POST.get(
                "date_of_birth",
                "",
            ).strip()
            if date_of_birth:
                try:
                    profile.date_of_birth = datetime.strptime(
                        date_of_birth,
                        "%Y-%m-%d",
                    ).date()
                except ValueError:
                    pass
            city_id = request.POST.get(
                "city",
                "",
            ).strip()
            profile.city = (
                City.objects.filter(
                    pk=city_id
                ).first()
                if city_id
                else None
            )
            profile_image = request.FILES.get(
                "profile_image"
            )
            if profile_image:
                if profile.profile_image:
                    profile.profile_image.delete(
                        save=False
                    )
                profile.profile_image = profile_image
            remove_profile_image = (
                request.POST.get(
                    "remove_profile_image"
                )
                == "1"
            )
            if remove_profile_image and profile.profile_image:
                profile.profile_image.delete(
                    save=False
                )
                profile.profile_image = None
            profile.save()
            address_line1 = request.POST.get(
                "address_line1",
                "",
            ).strip()
            address_line2 = request.POST.get(
                "address_line2",
                "",
            ).strip()
            landmark = request.POST.get(
                "landmark",
                "",
            ).strip()
            postal_code = request.POST.get(
                "postal_code",
                "",
            ).strip()
            label = request.POST.get(
                "address_label",
                "",
            ).strip()
            address_type = request.POST.get(
                "address_type",
                UserAddress.AddressType.OTHER,
            ).strip()
            address_city_id = (
                request.POST.get(
                    "address_city",
                    "",
                ).strip()
                or city_id
            )
            if address_line1:
                address = (
                    UserAddress.objects.filter(
                        user=saved_user,
                        is_default=True,
                    ).first()
                    or UserAddress.objects.filter(
                        user=saved_user
                    ).first()
                )
                if address is None:
                    address = UserAddress(
                        user=saved_user
                    )
                address.address_line1 = address_line1
                address.address_line2 = address_line2
                address.landmark = landmark
                address.postal_code = postal_code
                address.label = label
                address.address_type = address_type
                address.city = (
                    City.objects.filter(
                        pk=address_city_id
                    ).first()
                    if address_city_id
                    else None
                )
                address.is_default = True
                address.save()
                UserAddress.objects.filter(
                    user=saved_user
                ).exclude(
                    pk=address.pk
                ).update(
                    is_default=False
                )
            messages.success(
                request,
                "User saved successfully.",
            )
            return redirect(
                "user_list"
            )
    else:
        form = UserCreateForm(
            instance=user_obj
        )
    cities = City.objects.all().order_by(
        "name"
    )
    return render(
        request,
        "dashboard/users/user_create.html",
        {
            "form": form,
            "user_obj": user_obj,
            "selected_user": user_obj,
            "page_title": (
                "Edit User"
                if user_obj
                else "Add User"
            ),
            "cities": cities,
        },
    )


@login_required
def user_delete(request, pk):
    if request.method != "POST":
        return redirect("user_list")
    user_obj = get_object_or_404(
        User,
        pk=pk,
    )
    if user_obj.pk == request.user.pk:
        messages.error(
            request,
            "You cannot delete your own account.",
        )
        return redirect("user_list")
    user_obj.delete()
    messages.success(
        request,
        "User deleted successfully.",
    )
    return redirect("user_list")


@login_required
def gallery_delete(request, pk):
    if request.method != "POST":
        return redirect("ride_gallery")
    gallery = get_object_or_404(
        Gallery,
        pk=pk,
    )
    gallery.delete()
    messages.success(
        request,
        "Gallery image deleted successfully.",
    )
    return redirect("ride_gallery")


@login_required
def user_list(request):
    users = User.objects.all().order_by(
        "-date_joined"
    )
    return render(
        request,
        "dashboard/users/list.html",
        {
            "users": users,
        },
    )


@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(
        User,
        pk=user_id,
    )
    profile, _ = UserProfile.objects.get_or_create(
        user=profile_user
    )
    address = (
        UserAddress.objects.filter(
            user=profile_user,
            is_default=True,
        ).first()
        or UserAddress.objects.filter(
            user=profile_user
        ).first()
    )
    return render(
        request,
        "account/user_profile.html",
        {
            "profile_user": profile_user,
            "selected_user": profile_user,
            "user_obj": profile_user,
            "profile": profile,
            "address": address,
        },
    )


@login_required
def dashboard(request):
    total_users = User.objects.count()
    active_users = User.objects.filter(
        is_active=True
    ).count()
    total_rides = Ride.objects.count()
    total_ride_requests = RideRequest.objects.count()
    completed_rides = Ride.objects.filter(
        status=Ride.Status.COMPLETED
    ).count()
    cancelled_rides = Ride.objects.filter(
        status=Ride.Status.CANCELLED
    ).count()
    ongoing_rides = Ride.objects.filter(
        status__in=[
            Ride.Status.DRIVER_ASSIGNED,
            Ride.Status.DRIVER_ARRIVING,
            Ride.Status.DRIVER_ARRIVED,
            Ride.Status.STARTED,
        ]
    ).count()
    pending_rides = RideRequest.objects.filter(
        status__in=[
            RideRequest.Status.REQUESTED,
            RideRequest.Status.SEARCHING,
        ]
    ).count()
    total_drivers = Driver.objects.count()
    active_drivers = _safe_active_count(
        Driver
    )
    verified_drivers = _safe_verified_count(
        Driver
    )
    pending_driver_verification = (
        _safe_pending_verification_count(
            Driver
        )
    )
    total_vehicles = Vehicle.objects.count()
    active_vehicles = _safe_active_count(
        Vehicle
    )
    total_vehicle_types = VehicleType.objects.count()
    total_payments = Payment.objects.count()
    successful_payments = _safe_status_count(
        Payment,
        [
            "success",
            "successful",
            "completed",
            "paid",
            "SUCCESS",
            "SUCCESSFUL",
            "COMPLETED",
            "PAID",
        ],
    )
    pending_payments = _safe_status_count(
        Payment,
        [
            "pending",
            "processing",
            "PENDING",
            "PROCESSING",
        ],
    )
    failed_payments = _safe_status_count(
        Payment,
        [
            "failed",
            "failure",
            "FAILED",
            "FAILURE",
        ],
    )
    total_revenue = _safe_sum(
        Payment,
        [
            "amount",
            "total_amount",
            "paid_amount",
            "fare_amount",
            "price",
        ],
    )
    if total_revenue == Decimal("0"):
        completed_fare = RideRequest.objects.filter(
            status=RideRequest.Status.COMPLETED
        ).aggregate(
            total=Sum("estimated_fare")
        )
        completed_fare_value = (
            completed_fare["total"]
            or Decimal("0")
        )
        if completed_fare_value > 0:
            total_revenue = completed_fare_value
    total_refunds = _safe_sum(
        Refund,
        [
            "amount",
            "refund_amount",
            "total_amount",
        ],
    )
    refunded_payments = Refund.objects.count()
    total_fare_rules = FareRule.objects.count()
    active_fare_rules = _safe_active_count(
        FareRule
    )
    total_surge_pricing = SurgePricing.objects.count()
    active_surge_pricing = _safe_active_count(
        SurgePricing
    )
    total_fare_breakdowns = (
        FareBreakdown.objects.count()
    )
    total_coupons = Coupon.objects.count()
    active_coupons = _safe_active_count(
        Coupon
    )
    total_coupon_usage = (
        CouponUsage.objects.count()
    )
    total_support_tickets = (
        SupportTicket.objects.count()
    )
    open_tickets = _safe_status_count(
        SupportTicket,
        [
            "open",
            "pending",
            "OPEN",
            "PENDING",
        ],
    )
    in_progress_tickets = _safe_status_count(
        SupportTicket,
        [
            "in_progress",
            "processing",
            "assigned",
            "IN_PROGRESS",
            "PROCESSING",
            "ASSIGNED",
        ],
    )
    urgent_tickets = 0
    support_ticket_fields = _field_names(
        SupportTicket
    )
    if "priority" in support_ticket_fields:
        urgent_tickets = SupportTicket.objects.filter(
            priority__in=[
                "urgent",
                "high",
                "Urgent",
                "High",
                "URGENT",
                "HIGH",
            ]
        ).count()
    maintenance_vehicles = 0
    blocked_vehicles = 0
    vehicle_fields = _field_names(
        Vehicle
    )
    if "status" in vehicle_fields:
        maintenance_vehicles = Vehicle.objects.filter(
            status__in=[
                "maintenance",
                "under_maintenance",
                "Maintenance",
                "Under Maintenance",
            ]
        ).count()
        blocked_vehicles = Vehicle.objects.filter(
            status__in=[
                "blocked",
                "inactive",
                "Blocked",
                "Inactive",
            ]
        ).count()
    elif "is_maintenance" in vehicle_fields:
        maintenance_vehicles = Vehicle.objects.filter(
            is_maintenance=True
        ).count()
    elif "is_blocked" in vehicle_fields:
        blocked_vehicles = Vehicle.objects.filter(
            is_blocked=True
        ).count()
    total_locations = Location.objects.count()
    total_countries = Country.objects.count()
    total_states = State.objects.count()
    total_cities = City.objects.count()
    recent_rides = (
        Ride.objects
        .select_related(
            "passenger",
            "driver",
            "vehicle",
            "ride_request",
        )
        .order_by("-id")[:10]
    )
    ride_distribution = list(
        Ride.objects
        .filter(
            ride_request__vehicle_type__isnull=False
        )
        .values(
            name=F(
                "ride_request__vehicle_type__name"
            )
        )
        .annotate(
            count=Count("id")
        )
        .order_by("-count")
    )
    context = {
        "total_users": total_users,
        "active_users": active_users,
        "total_rides": total_rides,
        "total_ride_requests": total_ride_requests,
        "completed_rides": completed_rides,
        "cancelled_rides": cancelled_rides,
        "ongoing_rides": ongoing_rides,
        "pending_rides": pending_rides,
        "total_drivers": total_drivers,
        "active_drivers": active_drivers,
        "verified_drivers": verified_drivers,
        "pending_driver_verification": pending_driver_verification,
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "maintenance_vehicles": maintenance_vehicles,
        "blocked_vehicles": blocked_vehicles,
        "total_vehicle_types": total_vehicle_types,
        "total_payments": total_payments,
        "successful_payments": successful_payments,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,
        "refunded_payments": refunded_payments,
        "total_revenue": total_revenue,
        "total_refunds": total_refunds,
        "total_fare_rules": total_fare_rules,
        "active_fare_rules": active_fare_rules,
        "total_surge_pricing": total_surge_pricing,
        "active_surge_pricing": active_surge_pricing,
        "total_fare_breakdowns": total_fare_breakdowns,
        "total_coupons": total_coupons,
        "active_coupons": active_coupons,
        "total_coupon_usage": total_coupon_usage,
        "total_support_tickets": total_support_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "urgent_tickets": urgent_tickets,
        "total_locations": total_locations,
        "total_countries": total_countries,
        "total_states": total_states,
        "total_cities": total_cities,
        "recent_rides": recent_rides,
        "ride_distribution": ride_distribution,
        "users_count": total_users,
        "rides_count": total_rides,
        "drivers_count": total_drivers,
        "vehicles_count": total_vehicles,
        "revenue": total_revenue,
    }
    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )


@login_required
@transaction.atomic
def user_setting(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(
        user=user
    )
    notification_preferences, _ = (
        AccountNotificationPreference.objects.get_or_create(
            user=user
        )
    )
    payment_detail, _ = (
        AccountPaymentDetail.objects.get_or_create(
            user=user
        )
    )
    address = (
        UserAddress.objects.filter(
            user=user,
            is_default=True,
        ).first()
        or UserAddress.objects.filter(
            user=user
        ).first()
    )
    verify_token = request.GET.get(
        "verify",
        "",
    ).strip()
    if verify_token:
        try:
            payload = loads(
                verify_token,
                salt=EMAIL_VERIFICATION_SALT,
                max_age=EMAIL_VERIFICATION_MAX_AGE,
            )
            if (
                int(payload.get("user_id")) == user.pk
                and payload.get("email") == user.email
            ):
                profile.email_verified = True
                profile.email_verified_at = timezone.now()
                profile.save(
                    update_fields=[
                        "email_verified",
                        "email_verified_at",
                        "updated_at",
                    ]
                )
                messages.success(
                    request,
                    "Email address verified successfully.",
                )
            else:
                messages.error(
                    request,
                    "This email verification link is invalid.",
                )
        except (
            SignatureExpired,
            BadSignature,
            TypeError,
            ValueError,
        ):
            messages.error(
                request,
                "This email verification link is invalid or expired.",
            )
        return redirect("user_setting")
    if request.method == "POST":
        action = request.POST.get(
            "action",
            "update_profile",
        ).strip()
        if action == "update_notification":
            field = request.POST.get(
                "field",
                "",
            ).strip()
            value = (
                request.POST.get(
                    "value",
                    "",
                ).lower()
                == "true"
            )
            allowed_fields = {
                "platform_updates",
                "security_alerts",
                "ride_activity",
                "email_notifications",
            }
            if field not in allowed_fields:
                return _json_error(
                    "Invalid notification field."
                )
            setattr(
                notification_preferences,
                field,
                value,
            )
            notification_preferences.save(
                update_fields=[
                    field,
                ]
            )
            return _json_success(
                "Notification preference updated.",
                field=field,
                value=value,
            )
        if action == "update_notifications":
            allowed_fields = {
                "platform_updates",
                "security_alerts",
                "ride_activity",
                "email_notifications",
            }
            for field in allowed_fields:
                if field in request.POST:
                    setattr(
                        notification_preferences,
                        field,
                        request.POST.get(
                            field
                        ).lower()
                        == "true",
                    )
            notification_preferences.save()
            messages.success(
                request,
                "Notification preferences updated.",
            )
            return redirect("user_setting")
        if action == "send_email_verification":
            if not user.email:
                return _json_error(
                    "Please add an email address first."
                )
            if profile.email_verified:
                return _json_success(
                    "Your email address is already verified.",
                    email_verified=True,
                )
            token = dumps(
                {
                    "user_id": user.pk,
                    "email": user.email,
                },
                salt=EMAIL_VERIFICATION_SALT,
            )
            query_string = urlencode(
                {
                    "verify": token,
                }
            )
            verification_url = request.build_absolute_uri(
                f"{reverse('user_setting')}?{query_string}"
            )
            subject = (
                "Verify your NandiRide email address"
            )
            message = (
                f"Hello {user.get_full_name() or user.get_username()},\n\n"
                "Please verify your NandiRide email address by opening the link below:\n\n"
                f"{verification_url}\n\n"
                "This verification link is valid for 24 hours.\n\n"
                "Regards,\n"
                "NandiRide"
            )
            try:
                send_mail(
                    subject,
                    message,
                    getattr(
                        settings,
                        "DEFAULT_FROM_EMAIL",
                        "webmaster@localhost",
                    ),
                    [user.email],
                    fail_silently=False,
                )
            except Exception:
                return _json_error(
                    "Verification email could not be sent. Please check your email settings."
                )
            return _json_success(
                "Verification email sent successfully. Please check your inbox.",
                email_verified=False,
            )
        if action == "save_account_details":
            upi_id = request.POST.get(
                "upi_id",
                "",
            ).strip()
            if upi_id:
                if len(upi_id) > 100:
                    return _json_error(
                        "UPI ID is too long."
                    )
                if not re.match(
                    r"^[A-Za-z0-9][A-Za-z0-9._-]{1,}@[A-Za-z0-9.-]{2,}$",
                    upi_id,
                ):
                    return _json_error(
                        "Please enter a valid UPI ID."
                    )
            payment_detail.upi_id = upi_id
            payment_detail.save(
                update_fields=[
                    "upi_id",
                    "updated_at",
                ]
            )
            return _json_success(
                (
                    "UPI ID linked successfully."
                    if upi_id
                    else "UPI ID removed successfully."
                ),
                upi_id=payment_detail.upi_id,
                has_upi=bool(payment_detail.upi_id),
                upi_status=(
                    "Linked"
                    if payment_detail.upi_id
                    else "Not Linked"
                ),
            )
        if action == "get_account_details":
            return _json_success(
                "Account details loaded.",
                upi_id=payment_detail.upi_id,
                upi_status=(
                    "Linked"
                    if payment_detail.upi_id
                    else "Not Linked"
                ),
                wallet_balance=f"{payment_detail.wallet_balance:.2f}",
                card_last_four=payment_detail.card_last_four,
                card_brand=payment_detail.card_brand,
                card_expiry=payment_detail.card_expiry,
                has_upi=bool(payment_detail.upi_id),
                has_card=bool(
                    payment_detail.card_last_four
                ),
            )
        if action == "add_wallet_money":
            amount_raw = request.POST.get(
                "amount",
                "",
            ).strip()
            try:
                amount = Decimal(amount_raw)
            except (
                InvalidOperation,
                TypeError,
            ):
                return _json_error(
                    "Please enter a valid amount."
                )
            if amount <= 0:
                return _json_error(
                    "Wallet amount must be greater than zero."
                )
            if amount.as_tuple().exponent < -2:
                return _json_error(
                    "Wallet amount can have maximum 2 decimal places."
                )
            with transaction.atomic():
                locked_payment_detail = (
                    AccountPaymentDetail.objects.select_for_update().get(
                        pk=payment_detail.pk
                    )
                )
                locked_payment_detail.wallet_balance += amount
                locked_payment_detail.save(
                    update_fields=[
                        "wallet_balance",
                        "updated_at",
                    ]
                )
                wallet_transaction = WalletTransaction.objects.create(
                    user=user,
                    transaction_type=WalletTransaction.TransactionType.CREDIT,
                    amount=amount,
                    balance_after=locked_payment_detail.wallet_balance,
                    status=WalletTransaction.Status.SUCCESS,
                    description="Wallet balance added from Account Settings.",
                )
                wallet_balance = (
                    locked_payment_detail.wallet_balance
                )
            transaction_date = getattr(
                wallet_transaction,
                "created_at",
                None,
            )
            if transaction_date is None:
                transaction_date = getattr(
                    wallet_transaction,
                    "created",
                    None,
                )
            if transaction_date is None:
                transaction_date = timezone.now()
            transaction_type = getattr(
                wallet_transaction.transaction_type,
                "label",
                None,
            ) or "Credit"
            transaction_status = getattr(
                wallet_transaction.status,
                "label",
                None,
            ) or "Success"
            return _json_success(
                "Money added to wallet successfully.",
                wallet_balance=f"{wallet_balance:.2f}",
                amount_added=f"{amount:.2f}",
                transaction={
                    "id": wallet_transaction.pk,
                    "date": transaction_date.strftime(
                        "%d %b %Y, %I:%M %p"
                    ),
                    "type": str(transaction_type),
                    "amount": f"{amount:.2f}",
                    "balance": f"{wallet_balance:.2f}",
                    "status": str(transaction_status),
                    "description": wallet_transaction.description,
                },
            )
        if action == "save_card":
            card_last_four = request.POST.get(
                "card_last_four",
                "",
            ).strip()
            card_brand = request.POST.get(
                "card_brand",
                "",
            ).strip()
            card_expiry = request.POST.get(
                "card_expiry",
                "",
            ).strip()
            if (
                not card_last_four.isdigit()
                or len(card_last_four) != 4
            ):
                return _json_error(
                    "Please enter the last 4 digits of your card."
                )
            if not card_brand:
                return _json_error(
                    "Please select or enter the card brand."
                )
            if len(card_brand) > 30:
                return _json_error(
                    "Card brand is too long."
                )
            if not re.match(
                r"^(0[1-9]|1[0-2])/(?:[0-9]{2}|[0-9]{4})$",
                card_expiry,
            ):
                return _json_error(
                    "Card expiry must be in MM/YY or MM/YYYY format."
                )
            payment_detail.card_last_four = card_last_four
            payment_detail.card_brand = card_brand
            payment_detail.card_expiry = card_expiry
            payment_detail.save(
                update_fields=[
                    "card_last_four",
                    "card_brand",
                    "card_expiry",
                    "updated_at",
                ]
            )
            return _json_success(
                "Card details saved successfully.",
                card_last_four=payment_detail.card_last_four,
                card_brand=payment_detail.card_brand,
                card_expiry=payment_detail.card_expiry,
                has_card=True,
            )
        if action == "remove_card":
            payment_detail.card_last_four = ""
            payment_detail.card_brand = ""
            payment_detail.card_expiry = ""
            payment_detail.save(
                update_fields=[
                    "card_last_four",
                    "card_brand",
                    "card_expiry",
                    "updated_at",
                ]
            )
            return _json_success(
                "Card removed successfully.",
                has_card=False,
                card_last_four="",
                card_brand="",
                card_expiry="",
            )
        if action == "change_password":
            current_password = request.POST.get(
                "current_password",
                "",
            )
            new_password = request.POST.get(
                "new_password",
                "",
            )
            confirm_password = request.POST.get(
                "confirm_password",
                "",
            )
            if not user.check_password(
                current_password
            ):
                messages.error(
                    request,
                    "Current password is incorrect.",
                )
                return redirect("user_setting")
            if len(new_password) < 8:
                messages.error(
                    request,
                    "New password must contain at least 8 characters.",
                )
                return redirect("user_setting")
            if new_password != confirm_password:
                messages.error(
                    request,
                    "New password and confirmation password do not match.",
                )
                return redirect("user_setting")
            user.set_password(new_password)
            user.save(
                update_fields=[
                    "password",
                ]
            )
            update_session_auth_hash(
                request,
                user,
            )
            messages.success(
                request,
                "Password changed successfully.",
            )
            return redirect("user_setting")
        old_email = user.email.strip()
        new_email = request.POST.get(
            "email",
            user.email,
        ).strip()
        user.first_name = request.POST.get(
            "first_name",
            user.first_name,
        ).strip()
        user.last_name = request.POST.get(
            "last_name",
            user.last_name,
        ).strip()
        user.email = new_email
        user.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
            ]
        )
        if new_email != old_email:
            profile.email_verified = False
            profile.email_verified_at = None
        profile.phone = request.POST.get(
            "phone",
            profile.phone,
        ).strip()
        profile.gender = request.POST.get(
            "gender",
            profile.gender,
        ).strip()
        profile.address = request.POST.get(
            "address",
            profile.address,
        ).strip()
        profile.emergency_contact_name = request.POST.get(
            "emergency_contact_name",
            profile.emergency_contact_name,
        ).strip()
        profile.emergency_contact_phone = request.POST.get(
            "emergency_contact_phone",
            profile.emergency_contact_phone,
        ).strip()
        date_of_birth = request.POST.get(
            "date_of_birth",
            "",
        ).strip()
        if date_of_birth:
            try:
                profile.date_of_birth = datetime.strptime(
                    date_of_birth,
                    "%Y-%m-%d",
                ).date()
            except ValueError:
                pass
        city_id = request.POST.get(
            "city",
            "",
        ).strip()
        profile.city = (
            City.objects.filter(
                pk=city_id
            ).first()
            if city_id
            else None
        )
        remove_profile_image = (
            request.POST.get(
                "remove_profile_image"
            )
            == "1"
        )
        profile_image = request.FILES.get(
            "profile_image"
        )
        if remove_profile_image:
            if profile.profile_image:
                profile.profile_image.delete(
                    save=False
                )
            profile.profile_image = None
        elif profile_image:
            if profile.profile_image:
                profile.profile_image.delete(
                    save=False
                )
            profile.profile_image = profile_image
        profile.save()
        address_line1 = request.POST.get(
            "address_line1",
            "",
        ).strip()
        address_line2 = request.POST.get(
            "address_line2",
            "",
        ).strip()
        landmark = request.POST.get(
            "landmark",
            "",
        ).strip()
        postal_code = request.POST.get(
            "postal_code",
            "",
        ).strip()
        label = request.POST.get(
            "address_label",
            "",
        ).strip()
        address_type = request.POST.get(
            "address_type",
            UserAddress.AddressType.OTHER,
        ).strip()
        address_city_id = (
            request.POST.get(
                "address_city",
                "",
            ).strip()
            or city_id
        )
        remove_address = (
            request.POST.get(
                "remove_address"
            )
            == "1"
        )
        if address_line1:
            if address is None:
                address = UserAddress(
                    user=user
                )
            address.address_line1 = address_line1
            address.address_line2 = address_line2
            address.landmark = landmark
            address.postal_code = postal_code
            address.label = label
            address.address_type = address_type
            address.city = (
                City.objects.filter(
                    pk=address_city_id
                ).first()
                if address_city_id
                else None
            )
            address.is_default = True
            address.save()
            UserAddress.objects.filter(
                user=user
            ).exclude(
                pk=address.pk
            ).update(
                is_default=False
            )
        elif remove_address and address:
            address.delete()
            address = None
        messages.success(
            request,
            "Account settings updated successfully.",
        )
        return redirect("user_setting")
    cities = City.objects.all().order_by(
        "name"
    )
    return render(
        request,
        "account/setting.html",
        {
            "user": user,
            "profile": profile,
            "address": address,
            "cities": cities,
            "notification_preferences": notification_preferences,
            "payment_detail": payment_detail,
            "payment_details": payment_detail,
            "email_verified": bool(
                profile.email_verified
                and user.email
            ),
        },
    )


@login_required
def group_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        if not group_id:
            return JsonResponse({
                "success": False,
                "message": "Group ID is required."
            }, status=400)
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Group not found."
            }, status=404)
        group_status, created = GroupStatus.objects.get_or_create(
            group=group,
            defaults={"is_active": True}
        )
        group_status.is_active = not group_status.is_active
        group_status.save(update_fields=["is_active", "updated_at"])
        return JsonResponse({
            "success": True,
            "group_id": group.id,
            "is_active": group_status.is_active,
            "status": "Active" if group_status.is_active else "Inactive"
        })
    query = request.GET.get("q", "").strip()
    groups = Group.objects.all().order_by("name")
    if query:
        groups = groups.filter(Q(name__icontains=query))
    for group in groups:
        group.group_status = GroupStatus.objects.get_or_create(
            group=group,
            defaults={"is_active": True}
        )[0]
    context = {
        "groups": groups,
        "total_users": User.objects.count(),
        "assigned_users": User.objects.filter(groups__isnull=False).distinct().count(),
        "total_permissions": Permission.objects.count(),
        "page_title": "Groups Management",
    }
    return render(request, "dashboard/groups.html", context)