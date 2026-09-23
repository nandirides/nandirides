from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
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
    CancellationReason,
    Ride,
    RideCancellation,
    RideDriverAssignment,
    RideRating,
    RideRequest,
    RideStop,
    RideTracking,
)
try:
    from payments.models import Payment
except (ImportError, ModuleNotFoundError):
    Payment = None
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
def _paginate(request, queryset, default_per_page=15):
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page
    per_page = max(5, min(per_page, 100))
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
def _ride_request_queryset():
    return RideRequest.objects.select_related(
        "passenger",
        "pickup_location",
        "drop_location",
        "vehicle_type",
    ).order_by("-requested_at", "-pk")
def _ride_queryset():
    return Ride.objects.select_related(
        "ride_request",
        "passenger",
        "driver",
        "vehicle",
        "pickup_location",
        "drop_location",
    ).order_by("-created_at", "-pk")
def _model_text_fields(model):
    """
    Return only concrete text-based fields from a model.
    This avoids invalid lookups such as:
    pickup_location__name__icontains
    when the Location model does not contain a name field.
    """
    text_field_names = []
    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if getattr(field, "many_to_many", False):
            continue
        if getattr(field, "one_to_many", False):
            continue
        internal_type = field.get_internal_type()
        if internal_type in {
            "CharField",
            "TextField",
            "EmailField",
            "SlugField",
        }:
            text_field_names.append(field.name)
    return text_field_names
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
    for field_name in _model_text_fields(user_model):
        q_objects.append(
            Q(
                **{
                    f"{relation_name}__{field_name}__icontains": query
                }
            )
        )
def _driver_search(q_objects, query):
    try:
        driver_field = Ride._meta.get_field("driver")
        driver_model = driver_field.remote_field.model
    except Exception:
        return
    for field_name in _model_text_fields(driver_model):
        q_objects.append(
            Q(
                **{
                    f"driver__{field_name}__icontains": query
                }
            )
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
    _driver_search(
        q_objects,
        query,
    )
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
    if not q_objects:
        return queryset.none()
    combined_query = q_objects[0]
    for item in q_objects[1:]:
        combined_query |= item
    return queryset.filter(
        combined_query
    ).distinct()
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
    if not q_objects:
        return queryset.none()
    combined_query = q_objects[0]
    for item in q_objects[1:]:
        combined_query |= item
    return queryset.filter(
        combined_query
    ).distinct()
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
    return transitions.get(ride.status, [])
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
    new_status = mapping.get(ride.status)
    if new_status and ride_request.status != new_status:
        ride_request.status = new_status
        ride_request.save(
            update_fields=["status"]
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
            return (
                Payment.objects
                .filter(ride=ride)
                .order_by("-pk")
                .first()
            )
        if "ride_request" in payment_field_names:
            return (
                Payment.objects
                .filter(
                    ride_request=ride.ride_request
                )
                .order_by("-pk")
                .first()
            )
    except Exception:
        return None
    return None
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
def ride_request_create_edit(request, pk=None):
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
            saved_request = form.save()
            messages.success(
                request,
                f"Ride request {saved_request.request_number} has been "
                f"{'updated' if ride_request else 'created'} successfully.",
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
                    else reverse("ride_request_add")
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
    context = {
        "page_title": f"Ride Request {ride_request.request_number}",
        "breadcrumb_items": [
            {
                "title": "Ride Request",
                "url": "ride_request_list",
            },
        ],
        "ride_request": ride_request,
        "ride": ride,
        "linked_ride": ride,
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
            "This ride request cannot be deleted because a ride is linked to it.",
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
    ride_request.status = new_status
    ride_request.save(
        update_fields=["status"]
    )
    messages.success(
        request,
        f"Ride request {ride_request.request_number} status updated to "
        f"{ride_request.get_status_display()}.",
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
        "page_title": "Rides",
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
        request.GET.get("ride_request")
        or request.POST.get("ride_request")
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
            saved_ride = form.save()
            _sync_request_status_from_ride(
                saved_ride
            )
            messages.success(
                request,
                f"Ride {saved_ride.ride_number} has been "
                f"{'updated' if ride else 'created'} successfully.",
            )
            return redirect(
                "ride_details",
                pk=saved_ride.pk,
            )
    else:
        initial = {}
        if source_request and not ride:
            initial = {
                "ride_request": source_request.pk,
                "passenger": source_request.passenger_id,
                "pickup_location": source_request.pickup_location_id,
                "drop_location": source_request.drop_location_id,
                "scheduled_at": source_request.scheduled_at,
            }
            form = RideForm(
                instance=ride,
                initial=initial,
            )
        else:
            form = RideForm(
                instance=ride
            )
    context = {
        "page_title": (
            "Edit Ride"
            if ride
            else "Create Ride"
        ),
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
            if allowed and new_status not in allowed:
                messages.error(
                    request,
                    "This status transition is not allowed from the current ride status.",
                )
            else:
                old_status = ride.status
                ride.status = new_status
                now = timezone.now()
                if new_status == Ride.Status.DRIVER_ARRIVED:
                    ride.arrived_at = now
                elif new_status == Ride.Status.STARTED:
                    ride.started_at = ride.started_at or now
                elif new_status == Ride.Status.COMPLETED:
                    ride.completed_at = now
                ride.save()
                _sync_request_status_from_ride(
                    ride
                )
                messages.success(
                    request,
                    f"Ride {ride.ride_number} changed from "
                    f"{dict(Ride.Status.choices).get(old_status, old_status)} to "
                    f"{ride.get_status_display()}.",
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
        "page_title": f"Driver Assignments - {ride.ride_number}",
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
                ride.status == Ride.Status.DRIVER_ASSIGNED
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
        "page_title": f"Assign Driver - {ride.ride_number}",
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
        "page_title": f"Edit Assignment - {assignment.ride.ride_number}",
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
    if request.method == "POST":
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
        "page_title": f"Tracking - {ride.ride_number}",
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
    if request.method == "POST":
        tracking.delete()
        messages.success(
            request,
            "Tracking point deleted successfully.",
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
        form = RideCancellationForm(
            request.POST
        )
        if form.is_valid():
            with transaction.atomic():
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
            messages.success(
                request,
                f"Ride {ride.ride_number} has been cancelled successfully.",
            )
            return redirect(
                "ride_details",
                pk=ride.pk,
            )
    else:
        form = RideCancellationForm(
            initial={
                "cancelled_by": request.user.pk,
            }
        )
    context = {
        "page_title": f"Cancel Ride - {ride.ride_number}",
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
    if request.method == "POST":
        form = RideRatingForm(
            request.POST
        )
        if form.is_valid():
            rating = form.save(
                commit=False
            )
            rating.ride = ride
            if not rating.from_user_id:
                rating.from_user = request.user
            if not rating.to_user_id and ride.driver_id:
                try:
                    rating.to_user = ride.driver.user
                except AttributeError:
                    pass
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
        initial = {
            "from_user": request.user.pk,
        }
        if ride.driver_id:
            try:
                initial["to_user"] = ride.driver.user.pk
            except AttributeError:
                pass
        form = RideRatingForm(
            initial=initial
        )
    context = {
        "page_title": f"Rate Ride - {ride.ride_number}",
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
        "page_title": f"Ride Stops - {ride.ride_number}",
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
        "page_title": f"Add Stop - {ride.ride_number}",
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
        "page_title": f"Edit Stop - {stop.ride.ride_number}",
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
    if request.method == "POST":
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
    total_requests = RideRequest.objects.count()
    requested_requests = RideRequest.objects.filter(
        status=RideRequest.Status.REQUESTED
    ).count()
    searching_requests = RideRequest.objects.filter(
        status=RideRequest.Status.SEARCHING
    ).count()
    assigned_requests = RideRequest.objects.filter(
        status=RideRequest.Status.ASSIGNED
    ).count()
    accepted_requests = RideRequest.objects.filter(
        status=RideRequest.Status.ACCEPTED
    ).count()
    cancelled_requests = RideRequest.objects.filter(
        status=RideRequest.Status.CANCELLED
    ).count()
    expired_requests = RideRequest.objects.filter(
        status=RideRequest.Status.EXPIRED
    ).count()
    completed_requests = RideRequest.objects.filter(
        status=RideRequest.Status.COMPLETED
    ).count()
    total_rides = Ride.objects.count()
    driver_assigned_rides = Ride.objects.filter(
        status=Ride.Status.DRIVER_ASSIGNED
    ).count()
    driver_arriving_rides = Ride.objects.filter(
        status=Ride.Status.DRIVER_ARRIVING
    ).count()
    driver_arrived_rides = Ride.objects.filter(
        status=Ride.Status.DRIVER_ARRIVED
    ).count()
    started_rides = Ride.objects.filter(
        status=Ride.Status.STARTED
    ).count()
    active_rides = Ride.objects.filter(
        status__in=RIDE_ACTIVE_STATUSES
    ).count()
    completed_rides = Ride.objects.filter(
        status=Ride.Status.COMPLETED
    ).count()
    cancelled_rides = Ride.objects.filter(
        status=Ride.Status.CANCELLED
    ).count()
    recent_rides = _ride_queryset()[:10]
    recent_requests = _ride_request_queryset()[:10]
    context = {
        "page_title": "Ride Dashboard",
        "breadcrumb_items": [
            {
                "title": "Ride Dashboard",
                "url": "ride_dashboard",
            },
        ],
        "total_requests": total_requests,
        "requested_requests": requested_requests,
        "searching_requests": searching_requests,
        "assigned_requests": assigned_requests,
        "accepted_requests": accepted_requests,
        "cancelled_requests": cancelled_requests,
        "expired_requests": expired_requests,
        "completed_requests": completed_requests,
        "total_rides": total_rides,
        "active_rides": active_rides,
        "driver_assigned_rides": driver_assigned_rides,
        "driver_arriving_rides": driver_arriving_rides,
        "driver_arrived_rides": driver_arrived_rides,
        "started_rides": started_rides,
        "completed_rides": completed_rides,
        "cancelled_rides": cancelled_rides,
        "recent_rides": recent_rides,
        "recent_requests": recent_requests,
    }
    return render(
        request,
        "rides/ride_dashboard.html",
        context,
    )
