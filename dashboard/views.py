from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GalleryForm, UserCreateForm
from dashboard.models import Gallery, UserAddress, UserProfile
from drivers.models import Driver
from locations.models import City, Country, Location, State
from payments.models import Payment, Refund
from pricing.models import FareBreakdown, FareRule, SurgePricing
from promotions.models import Coupon, CouponUsage
from rides.models import Ride, RideRequest
from support.models import SupportTicket
from vehicles.models import Vehicle, VehicleType


# Gallery
@login_required
def ride_gallery(request):
    gallery = Gallery.objects.all().order_by("-date")
    if request.method == "POST":
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Gallery image uploaded successfully.")
            return redirect("ride_gallery")
    else:
        form = GalleryForm()
    return render(
        request,
        "includes/gallery.html",
        {
            "form": form,
            "gallery": gallery,
        },
    )


# User Create / Update
@login_required
@transaction.atomic
def user_create(request, pk=None):
    if pk is None:
        user_obj = None
        page_title = "Add User"
    else:
        user_obj = get_object_or_404(User, pk=pk)
        page_title = "Edit User"

    if request.method == "POST":
        if request.POST.get("action") == "toggle_status":
            if user_obj == request.user:
                messages.error(
                    request,
                    "You cannot change your own account status.",
                )
            else:
                user_obj.is_active = not user_obj.is_active
                user_obj.save(update_fields=["is_active"])
                status = "activated" if user_obj.is_active else "deactivated"
                messages.success(
                    request,
                    f"User '{user_obj.username}' has been {status} successfully.",
                )
            return redirect("user_list")

        form = UserCreateForm(
            request.POST,
            request.FILES,
            instance=user_obj,
        )

        if form.is_valid():
            user = form.save(commit=False)

            if user_obj:
                password1 = form.cleaned_data.get("password1")
                if password1:
                    user.set_password(password1)

            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = form.cleaned_data.get("phone", "")
            profile.date_of_birth = form.cleaned_data.get("date_of_birth")
            profile.gender = form.cleaned_data.get("gender", "")
            profile.city = form.cleaned_data.get("city")
            profile.address = form.cleaned_data.get("address", "")
            profile.emergency_contact_name = form.cleaned_data.get(
                "emergency_contact_name",
                "",
            )
            profile.emergency_contact_phone = form.cleaned_data.get(
                "emergency_contact_phone",
                "",
            )

            profile_image = form.cleaned_data.get("profile_image")

            if profile_image:
                old_profile_image = profile.profile_image
                profile.profile_image = profile_image

                if old_profile_image:
                    old_profile_image.delete(save=False)

            profile.save()

            address_line1 = form.cleaned_data.get(
                "address_line1",
                "",
            ).strip()

            if address_line1:
                address = UserAddress.objects.filter(
                    user=user,
                    is_default=True,
                ).first()

                if address is None:
                    address = UserAddress.objects.filter(
                        user=user,
                    ).first()

                if address is None:
                    address = UserAddress(user=user)

                address.address_type = form.cleaned_data.get(
                    "address_type",
                    UserAddress.AddressType.OTHER,
                )
                address.label = form.cleaned_data.get("label", "")
                address.address_line1 = address_line1
                address.address_line2 = form.cleaned_data.get(
                    "address_line2",
                    "",
                )
                address.landmark = form.cleaned_data.get(
                    "landmark",
                    "",
                )
                address.postal_code = form.cleaned_data.get(
                    "postal_code",
                    "",
                )
                address.city = form.cleaned_data.get("address_city")
                address.is_default = True
                address.save()

                UserAddress.objects.filter(
                    user=user,
                ).exclude(
                    pk=address.pk,
                ).update(
                    is_default=False,
                )

            if user_obj:
                messages.success(
                    request,
                    f"{user.username} updated successfully.",
                )
            else:
                messages.success(
                    request,
                    f"{user.username} created successfully.",
                )

            return redirect(
                "user_profile",
                user_id=user.pk,
            )
    else:
        form = UserCreateForm(instance=user_obj)

    return render(
        request,
        "dashboard/users/user_create.html",
        {
            "form": form,
            "user_obj": user_obj,
            "page_title": page_title,
        },
    )


# User Delete
@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method != "POST":
        return redirect("user_list")

    if user == request.user:
        messages.error(
            request,
            "You cannot delete your own account.",
        )
        return redirect("user_list")

    username = user.username
    user.delete()

    messages.success(
        request,
        f"User '{username}' deleted successfully.",
    )

    return redirect("user_list")


# Gallery Delete
@login_required
def gallery_delete(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)

    if request.method != "POST":
        return redirect("ride_gallery")

    gallery.delete()

    messages.success(
        request,
        "Gallery image deleted successfully.",
    )

    return redirect("ride_gallery")


# Dashboard
@login_required
def dashboard(request):
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()

    total_rides = Ride.objects.count()
    completed_rides = Ride.objects.filter(
        status=Ride.Status.COMPLETED
    ).count()

    ongoing_rides = Ride.objects.filter(
        status__in=[
            Ride.Status.DRIVER_ASSIGNED,
            Ride.Status.DRIVER_ARRIVING,
            Ride.Status.DRIVER_ARRIVED,
            Ride.Status.STARTED,
        ]
    ).count()

    cancelled_rides = Ride.objects.filter(
        status=Ride.Status.CANCELLED
    ).count()

    total_ride_requests = RideRequest.objects.count()
    requested_rides = RideRequest.objects.filter(
        status=RideRequest.Status.REQUESTED
    ).count()

    searching_rides = RideRequest.objects.filter(
        status=RideRequest.Status.SEARCHING
    ).count()

    assigned_requests = RideRequest.objects.filter(
        status=RideRequest.Status.ASSIGNED
    ).count()

    accepted_requests = RideRequest.objects.filter(
        status=RideRequest.Status.ACCEPTED
    ).count()

    pending_rides = RideRequest.objects.filter(
        status__in=[
            RideRequest.Status.REQUESTED,
            RideRequest.Status.SEARCHING,
        ]
    ).count()

    completed_requests = RideRequest.objects.filter(
        status=RideRequest.Status.COMPLETED
    ).count()

    cancelled_requests = RideRequest.objects.filter(
        status=RideRequest.Status.CANCELLED
    ).count()

    expired_requests = RideRequest.objects.filter(
        status=RideRequest.Status.EXPIRED
    ).count()

    total_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(
        status=Driver.Status.ACTIVE
    ).count()

    pending_drivers = Driver.objects.filter(
        status=Driver.Status.PENDING
    ).count()

    inactive_drivers = Driver.objects.filter(
        status=Driver.Status.INACTIVE
    ).count()

    suspended_drivers = Driver.objects.filter(
        status=Driver.Status.SUSPENDED
    ).count()

    blocked_drivers = Driver.objects.filter(
        status=Driver.Status.BLOCKED
    ).count()

    verified_drivers = Driver.objects.filter(
        verification_status=Driver.VerificationStatus.VERIFIED
    ).count()

    pending_driver_verification = Driver.objects.filter(
        verification_status=Driver.VerificationStatus.PENDING
    ).count()

    rejected_driver_verification = Driver.objects.filter(
        verification_status=Driver.VerificationStatus.REJECTED
    ).count()

    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(
        status=Vehicle.Status.ACTIVE
    ).count()

    inactive_vehicles = Vehicle.objects.filter(
        status=Vehicle.Status.INACTIVE
    ).count()

    maintenance_vehicles = Vehicle.objects.filter(
        status=Vehicle.Status.MAINTENANCE
    ).count()

    blocked_vehicles = Vehicle.objects.filter(
        status=Vehicle.Status.BLOCKED
    ).count()

    total_vehicle_types = VehicleType.objects.count()
    active_vehicle_types = VehicleType.objects.filter(
        is_active=True
    ).count()

    total_payments = Payment.objects.count()
    successful_payments = Payment.objects.filter(
        status=Payment.Status.SUCCESS
    ).count()

    pending_payments = Payment.objects.filter(
        status=Payment.Status.PENDING
    ).count()

    failed_payments = Payment.objects.filter(
        status=Payment.Status.FAILED
    ).count()

    refunded_payments = Payment.objects.filter(
        status=Payment.Status.REFUNDED
    ).count()

    total_revenue = Payment.objects.filter(
        status=Payment.Status.SUCCESS
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_refunds = Refund.objects.aggregate(
        total=Sum("refund_amount")
    )["total"] or 0

    total_fare_rules = FareRule.objects.count()
    active_fare_rules = FareRule.objects.filter(
        is_active=True
    ).count()

    total_surge_pricing = SurgePricing.objects.count()
    active_surge_pricing = SurgePricing.objects.filter(
        is_active=True
    ).count()

    total_fare_breakdowns = FareBreakdown.objects.count()

    total_coupons = Coupon.objects.count()
    active_coupons = Coupon.objects.filter(
        is_active=True
    ).count()

    total_coupon_usage = CouponUsage.objects.count()

    total_discount = CouponUsage.objects.aggregate(
        total=Sum("discount_amount")
    )["total"] or 0

    total_tickets = SupportTicket.objects.count()

    open_tickets = SupportTicket.objects.filter(
        status=SupportTicket.Status.OPEN
    ).count()

    in_progress_tickets = SupportTicket.objects.filter(
        status=SupportTicket.Status.IN_PROGRESS
    ).count()

    resolved_tickets = SupportTicket.objects.filter(
        status=SupportTicket.Status.RESOLVED
    ).count()

    closed_tickets = SupportTicket.objects.filter(
        status=SupportTicket.Status.CLOSED
    ).count()

    urgent_tickets = SupportTicket.objects.filter(
        priority=SupportTicket.Priority.URGENT
    ).count()

    total_countries = Country.objects.count()
    total_states = State.objects.count()
    total_cities = City.objects.count()
    total_locations = Location.objects.count()

    recent_rides = Ride.objects.select_related(
        "ride_request",
        "ride_request__vehicle_type",
        "passenger",
        "driver",
        "driver__user",
        "vehicle",
        "vehicle__vehicle_type",
    ).order_by("-id")[:5]

    vehicle_types = list(
        VehicleType.objects.order_by("name").values(
            "id",
            "name",
        )
    )

    ride_type_counts = Ride.objects.values(
        "ride_request__vehicle_type_id"
    ).annotate(
        total=Count("id")
    )

    ride_type_count_map = {
        item["ride_request__vehicle_type_id"]: item["total"]
        for item in ride_type_counts
    }

    ride_distribution = []

    for vehicle_type in vehicle_types:
        ride_distribution.append(
            {
                "name": vehicle_type["name"],
                "count": ride_type_count_map.get(
                    vehicle_type["id"],
                    0,
                ),
            }
        )

    context = {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "total_rides": total_rides,
        "completed_rides": completed_rides,
        "ongoing_rides": ongoing_rides,
        "cancelled_rides": cancelled_rides,
        "total_ride_requests": total_ride_requests,
        "requested_rides": requested_rides,
        "searching_rides": searching_rides,
        "assigned_requests": assigned_requests,
        "accepted_requests": accepted_requests,
        "pending_rides": pending_rides,
        "completed_requests": completed_requests,
        "cancelled_requests": cancelled_requests,
        "expired_requests": expired_requests,
        "total_drivers": total_drivers,
        "active_drivers": active_drivers,
        "pending_drivers": pending_drivers,
        "inactive_drivers": inactive_drivers,
        "suspended_drivers": suspended_drivers,
        "blocked_drivers": blocked_drivers,
        "verified_drivers": verified_drivers,
        "pending_driver_verification": pending_driver_verification,
        "rejected_driver_verification": rejected_driver_verification,
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "inactive_vehicles": inactive_vehicles,
        "maintenance_vehicles": maintenance_vehicles,
        "blocked_vehicles": blocked_vehicles,
        "total_vehicle_types": total_vehicle_types,
        "active_vehicle_types": active_vehicle_types,
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
        "total_discount": total_discount,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "urgent_tickets": urgent_tickets,
        "total_countries": total_countries,
        "total_states": total_states,
        "total_cities": total_cities,
        "total_locations": total_locations,
        "recent_rides": recent_rides,
        "ride_distribution": ride_distribution,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )


# Account Settings
@login_required
@transaction.atomic
def user_setting(request):
    user = request.user

    profile, created = UserProfile.objects.get_or_create(
        user=user
    )

    address = UserAddress.objects.filter(
        user=user,
        is_default=True,
    ).first()

    if address is None:
        address = UserAddress.objects.filter(
            user=user
        ).first()

    if request.method == "POST":
        action = request.POST.get(
            "action",
            "update_profile",
        )

        # Change Password
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

            if not user.check_password(current_password):
                messages.error(
                    request,
                    "Current password is incorrect.",
                )
                return redirect("user_setting")

            if not new_password:
                messages.error(
                    request,
                    "New password is required.",
                )
                return redirect("user_setting")

            if new_password != confirm_password:
                messages.error(
                    request,
                    "New password and confirm password do not match.",
                )
                return redirect("user_setting")

            if len(new_password) < 8:
                messages.error(
                    request,
                    "Password must contain at least 8 characters.",
                )
                return redirect("user_setting")

            if user.check_password(new_password):
                messages.error(
                    request,
                    "New password must be different from the current password.",
                )
                return redirect("user_setting")

            user.set_password(new_password)
            user.save(update_fields=["password"])

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Password changed successfully.",
            )

            return redirect("user_setting")

        # Update Basic Information
        user.first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        user.last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        user.email = request.POST.get(
            "email",
            "",
        ).strip()

        user.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
            ]
        )

        # Update Profile Information
        profile.phone = request.POST.get(
            "phone",
            "",
        ).strip()

        profile.gender = request.POST.get(
            "gender",
            "",
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
                messages.error(
                    request,
                    "Please enter a valid date of birth.",
                )
                return redirect("user_setting")
        else:
            profile.date_of_birth = None

        profile.address = request.POST.get(
            "address",
            "",
        ).strip()

        profile.emergency_contact_name = request.POST.get(
            "emergency_contact_name",
            "",
        ).strip()

        profile.emergency_contact_phone = request.POST.get(
            "emergency_contact_phone",
            "",
        ).strip()

        city_id = request.POST.get("city")

        profile.city = (
            City.objects.filter(
                pk=city_id
            ).first()
            if city_id
            else None
        )

        # Update Profile Image
        remove_profile_image = request.POST.get(
            "remove_profile_image"
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
            old_profile_image = profile.profile_image
            profile.profile_image = profile_image

            if old_profile_image:
                old_profile_image.delete(
                    save=False
                )

        profile.save()

        # Update Saved Address
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
            "label",
            "",
        ).strip()

        address_type = request.POST.get(
            "address_type",
            UserAddress.AddressType.OTHER,
        )

        address_city_id = request.POST.get(
            "address_city"
        ) or city_id

        if address_line1:
            if address is None:
                address = UserAddress(user=user)

            address.address_type = address_type
            address.label = label
            address.address_line1 = address_line1
            address.address_line2 = address_line2
            address.landmark = landmark
            address.postal_code = postal_code

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

        elif address is not None and request.POST.get(
            "remove_address"
        ):
            address.delete()
            address = None

        messages.success(
            request,
            "Account settings updated successfully.",
        )

        return redirect("user_setting")

    cities = City.objects.all().order_by("name")

    return render(
        request,
        "account/setting.html",
        {
            "user": user,
            "profile": profile,
            "address": address,
            "cities": cities,
        },
    )


# User Profile
@login_required
def user_profile(request, user_id):
    user = get_object_or_404(
        User,
        id=user_id,
    )

    profile = UserProfile.objects.filter(
        user=user
    ).first()

    address = UserAddress.objects.filter(
        user=user,
        is_default=True,
    ).first()

    return render(
        request,
        "account/user_profile.html",
        {
            "user": user,
            "profile": profile,
            "address": address,
        },
    )


# User List
@login_required
def user_list(request):
    users = User.objects.all()

    return render(
        request,
        "dashboard/users/list.html",
        {
            "users": users,
        },
    )
