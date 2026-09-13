from types import SimpleNamespace
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserCreateForm, GalleryForm
from dashboard.models import Gallery
from rides.models import Ride


def ride_gallery(request):
    gallery = Gallery.objects.all()
    if request.method == "POST":
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
def user_create(request, pk=None):
    # ADD USER
    if pk is None:
        user_obj = None
        page_title = "Add User"
    # UPDATE USER
    else:
        user_obj = get_object_or_404(
            User,
            pk=pk,
        )
        page_title = "Edit User"
    if request.method == "POST":
        form = UserCreateForm(
            request.POST,
            instance=user_obj,
        )
        if form.is_valid():
            user = form.save()
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
            return redirect("user_list")
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
    data = get_object_or_404(
        Gallery,
        pk=pk,
    )
    if request.method != "POST":
        return redirect("ride_gallery")
    image = data.profile_image
    data.delete()
    messages.success(
        request,
        f"User '{image}' Image deleted successfully.",
    )
    return redirect("ride_gallery")


@login_required
def dashboard(request):
    return render(
        request,
        "dashboard/dashboard.html",
    )


@login_required
def edit_admin_profile(request):
    return render(
        request,
        "account/edit_admin_profile.html",
    )


@login_required
def admin_profile(request):
    return render(
        request,
        "account/profile.html",
    )


@login_required
def user_profile(request, user_id):
    user = get_object_or_404(
        User,
        id=user_id,
    )
    return render(
        request,
        "account/user_profile.html",
        {
            "user": user,
        },
    )


@login_required
def user_setting(request):
    return render(
        request,
        "account/setting.html",
    )


@login_required
def user_ridestatus(request):
    rides = Ride.objects.select_related(
        "ride_request",
        "passenger",
        "driver",
        "vehicle",
        "pickup_location",
        "drop_location",
        "ride_request__vehicle_type",
    ).order_by("-id")
    active_statuses = [
        Ride.Status.DRIVER_ASSIGNED,
        Ride.Status.DRIVER_ARRIVING,
        Ride.Status.DRIVER_ARRIVED,
        Ride.Status.STARTED,
    ]
    on_track_statuses = [
        Ride.Status.DRIVER_ARRIVING,
        Ride.Status.DRIVER_ARRIVED,
        Ride.Status.STARTED,
    ]
    completed_status = Ride.Status.COMPLETED
    active_count = rides.filter(
        status__in=active_statuses,
    ).count()
    on_track_count = rides.filter(
        status__in=on_track_statuses,
    ).count()
    completed_count = rides.filter(
        status=completed_status,
    ).count()
    delayed_count = rides.filter(
        status=Ride.Status.CANCELLED,
    ).count()
    return render(
        request,
        "dashboard/users/ridestatus.html",
        {
            "rides": rides,
            "active_count": active_count,
            "on_track_count": on_track_count,
            "delayed_count": delayed_count,
            "completed_count": completed_count,
            "ride_count": rides.count(),
        },
    )


def get_demo_ride_details():
    passenger = SimpleNamespace(
        username="rahul",
        first_name="Rahul",
        last_name="Sharma",
        full_name="Rahul Sharma",
    )
    driver = SimpleNamespace(
        username="amit",
        first_name="Amit",
        last_name="Verma",
        full_name="Amit Verma",
    )
    vehicle = SimpleNamespace(
        registration_number="UP32AB1234",
        vehicle_number="UP32AB1234",
    )
    vehicle_type = SimpleNamespace(
        name="Bike",
    )
    ride_request = SimpleNamespace(
        request_number="REQ10001",
        vehicle_type=vehicle_type,
        requested_at="13 Sep 2026, 10:15 AM",
        scheduled_at="13 Sep 2026, 10:30 AM",
        estimated_distance="8.50",
        estimated_duration=25,
        estimated_fare="180.00",
    )
    ride = SimpleNamespace(
        id=1,
        ride_number="NR10001",
        status="started",
        status_display="Started",
        passenger=passenger,
        driver=driver,
        vehicle=vehicle,
        pickup_location="Lucknow Railway Station",
        drop_location="Hazratganj, Lucknow",
        scheduled_at="13 Sep 2026, 10:30 AM",
        started_at="13 Sep 2026, 10:35 AM",
        arrived_at="13 Sep 2026, 10:32 AM",
        completed_at=None,
        distance_km="5.40",
        duration_minutes=18,
        updated_at="13 Sep 2026, 10:53 AM",
        ride_request=ride_request,
    )
    stops = [
        SimpleNamespace(
            stop_order=1,
            location="Charbagh Crossing",
            arrival_time="13 Sep 2026, 10:42 AM",
            departure_time="13 Sep 2026, 10:44 AM",
            status="completed",
            status_display="Completed",
        ),
        SimpleNamespace(
            stop_order=2,
            location="Gomti Nagar",
            arrival_time="13 Sep 2026, 10:50 AM",
            departure_time=None,
            status="arrived",
            status_display="Arrived",
        ),
    ]
    driver_assignments = [
        SimpleNamespace(
            driver=driver,
            assigned_at="13 Sep 2026, 10:20 AM",
            accepted_at="13 Sep 2026, 10:22 AM",
            rejected_at=None,
            rejection_reason="",
            status="accepted",
            status_display="Accepted",
        ),
    ]
    ratings = [
        SimpleNamespace(
            from_user=passenger,
            to_user=driver,
            rating=5,
            review="Excellent ride and very professional driver.",
        ),
    ]
    tracking_points = [
        SimpleNamespace(
            driver=driver,
            latitude="26.846700",
            longitude="80.946200",
            speed="32.50",
            heading="90.00",
            accuracy="5.20",
            recorded_at="13 Sep 2026, 10:52 AM",
        ),
        SimpleNamespace(
            driver=driver,
            latitude="26.847100",
            longitude="80.947500",
            speed="29.80",
            heading="92.00",
            accuracy="4.80",
            recorded_at="13 Sep 2026, 10:53 AM",
        ),
    ]
    return {
        "ride": ride,
        "ride_request": ride_request,
        "stops": stops,
        "driver_assignments": driver_assignments,
        "tracking_points": tracking_points,
        "ratings": ratings,
        "cancellation": None,
        "is_demo": True,
    }


@login_required
def ride_details(request):
    ride = (
        Ride.objects
        .select_related(
            "ride_request",
            "passenger",
            "driver",
            "vehicle",
            "pickup_location",
            "drop_location",
            "ride_request__vehicle_type",
        )
        .prefetch_related(
            "stops__location",
            "driver_assignments__driver",
            "tracking_points__driver",
            "ratings__from_user",
            "ratings__to_user",
            "cancellation__cancelled_by",
            "cancellation__reason",
        )
        .order_by("-id")
        .first()
    )
    if ride:
        context = {
            "ride": ride,
            "ride_request": ride.ride_request,
            "stops": ride.stops.all(),
            "driver_assignments": ride.driver_assignments.all(),
            "tracking_points": ride.tracking_points.order_by("-recorded_at"),
            "ratings": ride.ratings.all(),
            "cancellation": getattr(
                ride,
                "cancellation",
                None,
            ),
            "is_demo": False,
        }
    else:
        context = get_demo_ride_details()
    return render(
        request,
        "dashboard/users/ride_details.html",
        context,
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


@login_required
def user_status_toggle(request, pk):
    user = get_object_or_404(
        User,
        pk=pk,
    )
    if request.method == "POST":
        if user == request.user:
            messages.error(
                request,
                "You cannot change your own account status.",
            )
            return redirect("user_list")
        user.is_active = not user.is_active
        user.save(
            update_fields=["is_active"],
        )
        status = "activated" if user.is_active else "deactivated"
        messages.success(
            request,
            f"User '{user.username}' has been {status} successfully.",
        )
    return redirect("user_list")