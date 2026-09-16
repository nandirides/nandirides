from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.db import transaction
from .forms import UserCreateForm, GalleryForm
from dashboard.models import Gallery, UserProfile, UserAddress
from locations.models import City
from rides.models import Ride, RideRequest
from payments.models import Payment


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
                "Gallery image uploaded successfully.",
            )
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


@login_required
@transaction.atomic
def user_create(request, pk=None):
    if pk is None:
        user_obj = None
        page_title = "Add User"
    else:
        user_obj = get_object_or_404(
            User,
            pk=pk,
        )
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
                user_obj.save(
                    update_fields=["is_active"],
                )
                status = (
                    "activated"
                    if user_obj.is_active
                    else "deactivated"
                )
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
            user = form.save(
                commit=False,
            )

            if user_obj:
                password1 = form.cleaned_data.get(
                    "password1",
                )
                if password1:
                    user.set_password(
                        password1,
                    )

            user.save()

            profile, created = UserProfile.objects.get_or_create(
                user=user,
            )

            profile.phone = form.cleaned_data.get(
                "phone",
                "",
            )
            profile.date_of_birth = form.cleaned_data.get(
                "date_of_birth",
            )
            profile.gender = form.cleaned_data.get(
                "gender",
                "",
            )
            profile.city = form.cleaned_data.get(
                "city",
            )
            profile.address = form.cleaned_data.get(
                "address",
                "",
            )
            profile.emergency_contact_name = form.cleaned_data.get(
                "emergency_contact_name",
                "",
            )
            profile.emergency_contact_phone = form.cleaned_data.get(
                "emergency_contact_phone",
                "",
            )

            profile_image = form.cleaned_data.get(
                "profile_image",
            )

            if profile_image:
                old_profile_image = profile.profile_image
                profile.profile_image = profile_image

                if old_profile_image:
                    old_profile_image.delete(
                        save=False,
                    )

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
                    address = UserAddress(
                        user=user,
                    )

                address.address_type = form.cleaned_data.get(
                    "address_type",
                    UserAddress.AddressType.OTHER,
                )
                address.label = form.cleaned_data.get(
                    "label",
                    "",
                )
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
                address.city = form.cleaned_data.get(
                    "address_city",
                )
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
        form = UserCreateForm(
            instance=user_obj,
        )
    return render(
        request,
        "dashboard/users/user_create.html",
        {
            "form": form,
            "user_obj": user_obj,
            "page_title": page_title,
        },
    )


@login_required
def user_delete(request, pk):
    user = get_object_or_404(
        User,
        pk=pk,
    )
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


@login_required
def gallery_delete(request, pk):
    gallery = get_object_or_404(
        Gallery,
        pk=pk,
    )
    if request.method != "POST":
        return redirect("ride_gallery")

    gallery.delete()

    messages.success(
        request,
        "Gallery image deleted successfully.",
    )
    return redirect("ride_gallery")


@login_required
def dashboard(request):
    # USER STATISTICS
    total_users = User.objects.count()

    active_users = User.objects.filter(
        is_active=True,
    ).count()

    inactive_users = User.objects.filter(
        is_active=False,
    ).count()

    # RIDE STATISTICS
    total_rides = Ride.objects.count()

    completed_rides = Ride.objects.filter(
        status=Ride.Status.COMPLETED,
    ).count()

    ongoing_rides = Ride.objects.filter(
        status__in=[
            Ride.Status.DRIVER_ASSIGNED,
            Ride.Status.DRIVER_ARRIVING,
            Ride.Status.DRIVER_ARRIVED,
            Ride.Status.STARTED,
        ],
    ).count()

    cancelled_rides = Ride.objects.filter(
        status=Ride.Status.CANCELLED,
    ).count()

    # RIDE REQUEST STATISTICS
    requested_rides = RideRequest.objects.filter(
        status=RideRequest.Status.REQUESTED,
    ).count()

    searching_rides = RideRequest.objects.filter(
        status=RideRequest.Status.SEARCHING,
    ).count()

    pending_rides = RideRequest.objects.filter(
        status__in=[
            RideRequest.Status.REQUESTED,
            RideRequest.Status.SEARCHING,
        ],
    ).count()

    # DRIVER STATISTICS
    active_drivers = User.objects.filter(
        is_active=True,
        groups__name="Driver",
    ).distinct().count()

    # PAYMENT STATISTICS
    total_revenue = Payment.objects.filter(
        status=Payment.Status.SUCCESS,
    ).aggregate(
        total=Sum("amount"),
    )["total"] or 0

    successful_payments = Payment.objects.filter(
        status=Payment.Status.SUCCESS,
    ).count()

    pending_payments = Payment.objects.filter(
        status=Payment.Status.PENDING,
    ).count()

    failed_payments = Payment.objects.filter(
        status=Payment.Status.FAILED,
    ).count()

    refunded_payments = Payment.objects.filter(
        status=Payment.Status.REFUNDED,
    ).count()

    # RECENT RIDES
    recent_rides = Ride.objects.select_related(
        "ride_request",
        "passenger",
        "driver",
        "vehicle",
        "ride_request__vehicle_type",
    ).order_by(
        "-id",
    )[:5]

    # RIDE DISTRIBUTION
    ride_distribution = {
        "bike": 0,
        "car": 0,
        "auto": 0,
        "premium": 0,
    }

    ride_types = Ride.objects.values(
        "ride_request__vehicle_type__name",
    ).annotate(
        total=Count("id"),
    )

    for item in ride_types:
        vehicle_name = (
            item["ride_request__vehicle_type__name"] or ""
        ).lower()

        ride_count = item["total"]

        if "bike" in vehicle_name:
            ride_distribution["bike"] += ride_count
        elif "auto" in vehicle_name:
            ride_distribution["auto"] += ride_count
        elif "premium" in vehicle_name:
            ride_distribution["premium"] += ride_count
        elif "car" in vehicle_name:
            ride_distribution["car"] += ride_count

    context = {
        # USERS
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,

        # RIDES
        "total_rides": total_rides,
        "completed_rides": completed_rides,
        "ongoing_rides": ongoing_rides,
        "cancelled_rides": cancelled_rides,

        # RIDE REQUESTS
        "requested_rides": requested_rides,
        "searching_rides": searching_rides,
        "pending_rides": pending_rides,

        # DRIVERS
        "active_drivers": active_drivers,

        # PAYMENTS
        "total_revenue": total_revenue,
        "successful_payments": successful_payments,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,
        "refunded_payments": refunded_payments,

        # RECENT RIDES
        "recent_rides": recent_rides,

        # CHART DATA
        "ride_distribution": ride_distribution,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )


@login_required
def edit_admin_profile(request):
    user = request.user

    profile, created = UserProfile.objects.get_or_create(
        user=user,
    )

    address = UserAddress.objects.filter(
        user=user,
        is_default=True,
    ).first()

    if address is None:
        address = UserAddress.objects.filter(
            user=user,
        ).first()

    if request.method == "POST":
        action = request.POST.get(
            "action",
        )

        # UPDATE PROFILE IMAGE DIRECTLY
        if action == "update_profile_image":
            profile_image = request.FILES.get(
                "profileimage",
            )

            if profile_image:
                old_profile_image = profile.profile_image
                profile.profile_image = profile_image

                profile.save(
                    update_fields=[
                        "profile_image",
                    ],
                )

                if old_profile_image:
                    old_profile_image.delete(
                        save=False,
                    )

                messages.success(
                    request,
                    "Profile photo updated successfully.",
                )
            else:
                messages.error(
                    request,
                    "Please select a photo.",
                )

            return redirect(
                "admin_profile",
            )

        # CHANGE ADMIN PASSWORD
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
                current_password,
            ):
                messages.error(
                    request,
                    "Current password is incorrect.",
                )
                return redirect(
                    "edit_admin_profile",
                )

            if not new_password:
                messages.error(
                    request,
                    "New password is required.",
                )
                return redirect(
                    "edit_admin_profile",
                )

            if new_password != confirm_password:
                messages.error(
                    request,
                    "New password and confirm password do not match.",
                )
                return redirect(
                    "edit_admin_profile",
                )

            if len(new_password) < 8:
                messages.error(
                    request,
                    "Password must contain at least 8 characters.",
                )
                return redirect(
                    "edit_admin_profile",
                )

            user.set_password(
                new_password,
            )

            user.save(
                update_fields=[
                    "password",
                ],
            )

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Admin password changed successfully.",
            )

            return redirect(
                "admin_profile",
            )

        # UPDATE USER INFORMATION
        user.username = request.POST.get(
            "username",
            "",
        ).strip()

        user.first_name = request.POST.get(
            "firstname",
            "",
        ).strip()

        user.last_name = request.POST.get(
            "lastname",
            "",
        ).strip()

        user.email = request.POST.get(
            "email",
            "",
        ).strip()

        user.save(
            update_fields=[
                "username",
                "first_name",
                "last_name",
                "email",
            ],
        )

        # UPDATE USER PROFILE
        profile.phone = request.POST.get(
            "mobilenumber",
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
                return redirect(
                    "edit_admin_profile",
                )
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

        # PROFILE CITY
        city_id = request.POST.get(
            "city",
        )

        if city_id:
            profile.city = City.objects.filter(
                pk=city_id,
            ).first()
        else:
            profile.city = None

        # PROFILE IMAGE
        remove_profile_image = request.POST.get(
            "remove_profile_image",
        )

        if remove_profile_image:
            if profile.profile_image:
                profile.profile_image.delete(
                    save=False,
                )

            profile.profile_image = None

        elif request.FILES.get(
            "profileimage",
        ):
            profile.profile_image = request.FILES[
                "profileimage"
            ]

        profile.save()

        # UPDATE USER ADDRESS
        address_line1 = request.POST.get(
            "address_line1",
            "",
        ).strip()

        if address is None and address_line1:
            address = UserAddress(
                user=user,
                is_default=True,
            )

        if address is not None:
            address.address_type = request.POST.get(
                "address_type",
                UserAddress.AddressType.OTHER,
            )

            address.label = request.POST.get(
                "label",
                "",
            ).strip()

            address.address_line1 = address_line1

            address.address_line2 = request.POST.get(
                "address_line2",
                "",
            ).strip()

            address.landmark = request.POST.get(
                "landmark",
                "",
            ).strip()

            address.postal_code = request.POST.get(
                "postal_code",
                "",
            ).strip()

            address_city_id = request.POST.get(
                "address_city",
            ) or request.POST.get(
                "city",
            )

            if address_city_id:
                address.city = City.objects.filter(
                    pk=address_city_id,
                ).first()
            else:
                address.city = None

            address.is_default = True

            address.save()

        messages.success(
            request,
            "Admin profile updated successfully.",
        )

        return redirect(
            "admin_profile",
        )

    cities = City.objects.all().order_by(
        "name",
    )

    return render(
        request,
        "account/edit_admin_profile.html",
        {
            "user": user,
            "profile": profile,
            "address": address,
            "cities": cities,
        },
    )


@login_required
def admin_profile(request):
    user = request.user

    profile = UserProfile.objects.filter(
        user=user,
    ).first()

    address = UserAddress.objects.filter(
        user=user,
        is_default=True,
    ).first()

    return render(
        request,
        "account/profile.html",
        {
            "user": user,
            "profile": profile,
            "address": address,
        },
    )


@login_required
def user_profile(request, user_id):
    user = get_object_or_404(
        User,
        id=user_id,
    )

    profile = UserProfile.objects.filter(
        user=user,
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


@login_required
def user_setting(request):
    return render(
        request,
        "account/setting.html",
    )

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
