from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from payments.models import Payment
from .forms import (
    RideCancellationForm,
    RideDriverAssignmentForm,
    RideForm,
    RideRatingForm,
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
def _ride_queryset():
    return (
        Ride.objects
        .select_related(
            "ride_request",
            "passenger",
            "driver",
            "driver__user",
            "vehicle",
            "vehicle__vehicle_type",
            "pickup_location",
            "drop_location",
        )
        .order_by("-created_at")
    )
def _paginate(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
def _ride_search_filter(queryset, search):
    if not search:
        return queryset
    return queryset.filter(
        Q(ride_number__icontains=search)
        | Q(ride_request__request_number__icontains=search)
        | Q(passenger__username__icontains=search)
        | Q(passenger__first_name__icontains=search)
        | Q(passenger__last_name__icontains=search)
        | Q(driver__driver_code__icontains=search)
        | Q(driver__user__username__icontains=search)
        | Q(driver__user__first_name__icontains=search)
        | Q(driver__user__last_name__icontains=search)
        | Q(vehicle__vehicle_number__icontains=search)
        | Q(pickup_location__address__icontains=search)
        | Q(drop_location__address__icontains=search)
    ).distinct()
def _live_statuses():
    return [
        Ride.Status.DRIVER_ASSIGNED,
        Ride.Status.DRIVER_ARRIVING,
        Ride.Status.DRIVER_ARRIVED,
        Ride.Status.STARTED,
    ]
def _allowed_next_statuses(current_status):
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
    return transitions.get(current_status, [])
@login_required
def ride_list(request):
    queryset = _ride_queryset()
    search = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()
    per_page = request.GET.get("per_page", "10")
    if search:
        queryset = _ride_search_filter(queryset, search)
    if selected_status:
        queryset = queryset.filter(status=selected_status)
    total_rides = Ride.objects.count()
    active_rides = Ride.objects.filter(
        status__in=_live_statuses()
    ).count()
    completed_rides = Ride.objects.filter(
        status=Ride.Status.COMPLETED
    ).count()
    cancelled_rides = Ride.objects.filter(
        status=Ride.Status.CANCELLED
    ).count()
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in [10, 25, 50]:
        per_page = 10
    page_obj = _paginate(
        queryset,
        request,
        per_page,
    )
    context = {
        "rides": page_obj.object_list,
        "page_obj": page_obj,
        "search": search,
        "selected_status": selected_status,
        "status_choices": Ride.Status.choices,
        "total_rides": total_rides,
        "active_rides": active_rides,
        "completed_rides": completed_rides,
        "cancelled_rides": cancelled_rides,
        "per_page": per_page,
    }
    return render(
        request,
        "rides/ride_list.html",
        context,
    )
@login_required
def ride_create_edit(request, pk=None):
    ride = None
    if pk is not None:
        ride = get_object_or_404(
            _ride_queryset(),
            pk=pk,
        )
    if request.method == "POST":
        form = RideForm(
            request.POST,
            instance=ride,
        )
        if form.is_valid():
            try:
                with transaction.atomic():
                    ride = form.save()
                    ride_request = ride.ride_request
                    if ride_request:
                        if ride_request.status in [
                            RideRequest.Status.REQUESTED,
                            RideRequest.Status.SEARCHING,
                        ]:
                            ride_request.status = RideRequest.Status.ASSIGNED
                            ride_request.save(
                                update_fields=[
                                    "status",
                                    "updated_at",
                                ]
                            )
                if pk:
                    messages.success(
                        request,
                        f"Ride {ride.ride_number} updated successfully.",
                    )
                else:
                    messages.success(
                        request,
                        f"Ride {ride.ride_number} created successfully.",
                    )
                return redirect(
                    "ride_details",
                    pk=ride.pk,
                )
            except ProtectedError:
                messages.error(
                    request,
                    "This ride cannot be saved because related records are protected.",
                )
            except Exception:
                messages.error(
                    request,
                    "Unable to save ride. Please check the form and try again.",
                )
        else:
            messages.error(
                request,
                "Please correct the errors below.",
            )
    else:
        form = RideForm(
            instance=ride,
        )
    context = {
        "form": form,
        "ride": ride,
        "page_title": "Edit Ride" if ride else "Add Ride",
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
    allowed_statuses = _allowed_next_statuses(
        ride.status
    )
    if request.method == "POST":
        form = RideStatusForm(
            request.POST
        )
        if form.is_valid():
            new_status = form.cleaned_data["status"]
            old_status = ride.status
            if old_status in [
                Ride.Status.COMPLETED,
                Ride.Status.CANCELLED,
            ]:
                messages.warning(
                    request,
                    "Completed or cancelled rides cannot be changed.",
                )
                return redirect(
                    "ride_details",
                    pk=ride.pk,
                )
            if new_status not in allowed_statuses:
                messages.warning(
                    request,
                    "This ride status transition is not allowed.",
                )
                return redirect(
                    "ride_status_update",
                    pk=ride.pk,
                )
            now = timezone.now()
            update_fields = [
                "status",
                "updated_at",
            ]
            ride.status = new_status
            if new_status == Ride.Status.DRIVER_ARRIVED:
                ride.arrived_at = now
                update_fields.append(
                    "arrived_at"
                )
            elif new_status == Ride.Status.STARTED:
                if not ride.started_at:
                    ride.started_at = now
                    update_fields.append(
                        "started_at"
                    )
            elif new_status == Ride.Status.COMPLETED:
                if not ride.started_at:
                    ride.started_at = now
                    update_fields.append(
                        "started_at"
                    )
                if not ride.completed_at:
                    ride.completed_at = now
                    update_fields.append(
                        "completed_at"
                    )
                if ride.started_at and ride.completed_at:
                    duration = (
                        ride.completed_at
                        - ride.started_at
                    ).total_seconds() / 60
                    if duration >= 0:
                        ride.duration_minutes = round(
                            duration
                        )
                        update_fields.append(
                            "duration_minutes"
                        )
                if ride.ride_request:
                    ride_request = ride.ride_request
                    if ride_request.status != RideRequest.Status.COMPLETED:
                        ride_request.status = RideRequest.Status.COMPLETED
                        ride_request.save(
                            update_fields=[
                                "status",
                                "updated_at",
                            ]
                        )
            elif new_status == Ride.Status.CANCELLED:
                ride_request = ride.ride_request
                if ride_request:
                    if ride_request.status not in [
                        RideRequest.Status.COMPLETED,
                        RideRequest.Status.CANCELLED,
                    ]:
                        ride_request.status = RideRequest.Status.CANCELLED
                        ride_request.save(
                            update_fields=[
                                "status",
                                "updated_at",
                            ]
                        )
            ride.save(
                update_fields=list(
                    dict.fromkeys(
                        update_fields
                    )
                )
            )
            messages.success(
                request,
                f"Ride status changed from "
                f"{old_status.replace('_', ' ').title()} "
                f"to "
                f"{new_status.replace('_', ' ').title()}.",
            )
            return redirect(
                "ride_details",
                pk=ride.pk,
            )
        messages.error(
            request,
            "Please select a valid ride status.",
        )
    else:
        form = RideStatusForm()
    form.fields["status"].choices = [
        (
            status,
            dict(Ride.Status.choices).get(
                status,
                status.replace(
                    "_",
                    " ",
                ).title(),
            ),
        )
        for status in allowed_statuses
    ]
    context = {
        "ride": ride,
        "form": form,
        "allowed_statuses": allowed_statuses,
        "page_title": "Update Ride Status",
    }
    return render(
        request,
        "rides/ride_status_update.html",
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
    if ride.status in [
        Ride.Status.STARTED,
        Ride.Status.COMPLETED,
    ]:
        messages.error(
            request,
            "Started or completed rides cannot be deleted.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    ride_number = ride.ride_number
    try:
        with transaction.atomic():
            ride.delete()
        messages.success(
            request,
            f"Ride {ride_number} deleted successfully.",
        )
    except ProtectedError:
        messages.error(
            request,
            "This ride cannot be deleted because related records exist.",
        )
    return redirect(
        "ride_list"
    )
@login_required
def ride_details(request, pk):
    ride = get_object_or_404(
        Ride.objects
        .select_related(
            "ride_request",
            "passenger",
            "driver",
            "driver__user",
            "vehicle",
            "vehicle__vehicle_type",
            "pickup_location",
            "drop_location",
        )
        .prefetch_related(
            "stops",
            "driver_assignments",
            "tracking_points",
            "ratings",
        ),
        pk=pk,
    )
    payment = (
        Payment.objects
        .filter(
            ride=ride
        )
        .order_by(
            "-created_at"
        )
        .first()
    )
    assignments = (
        ride.driver_assignments
        .select_related(
            "driver",
            "driver__user",
        )
        .order_by(
            "-assigned_at"
        )
    )
    latest_assignment = assignments.first()
    latest_tracking = (
        ride.tracking_points
        .order_by(
            "-recorded_at"
        )
        .first()
    )
    ratings = (
        ride.ratings
        .select_related(
            "from_user",
            "to_user",
        )
        .order_by(
            "-created_at"
        )
    )
    cancellation = getattr(
        ride,
        "cancellation",
        None,
    )
    stops = (
        ride.stops
        .select_related(
            "location"
        )
        .order_by(
            "stop_order"
        )
    )
    tracking_points = (
        ride.tracking_points
        .select_related(
            "driver"
        )
        .order_by(
            "-recorded_at"
        )
    )
    context = {
        "ride": ride,
        "payment": payment,
        "assignments": assignments,
        "latest_assignment": latest_assignment,
        "latest_tracking": latest_tracking,
        "tracking_points": tracking_points,
        "ratings": ratings,
        "cancellation": cancellation,
        "stops": stops,
        "allowed_statuses": _allowed_next_statuses(
            ride.status
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
        Ride.objects
        .select_related(
            "passenger",
            "driver",
            "driver__user",
            "vehicle",
            "vehicle__vehicle_type",
        ),
        pk=ride_pk,
    )
    assignments = (
        ride.driver_assignments
        .select_related(
            "driver",
            "driver__user",
        )
        .order_by(
            "-assigned_at"
        )
    )
    context = {
        "ride": ride,
        "assignments": assignments,
    }
    return render(
        request,
        "rides/assignment_list.html",
        context,
    )
@login_required
def ride_assignment_create(request, ride_pk):
    ride = get_object_or_404(
        Ride.objects
        .select_related(
            "passenger",
            "driver",
            "vehicle",
            "vehicle__vehicle_type",
        ),
        pk=ride_pk,
    )
    if ride.status in [
        Ride.Status.COMPLETED,
        Ride.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "Driver cannot be assigned to a completed or cancelled ride.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
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
            duplicate = (
                RideDriverAssignment.objects
                .filter(
                    ride=ride,
                    driver=assignment.driver,
                    status__in=[
                        RideDriverAssignment.Status.ASSIGNED,
                        RideDriverAssignment.Status.ACCEPTED,
                    ],
                )
                .exists()
            )
            if duplicate:
                form.add_error(
                    "driver",
                    "This driver is already assigned to this ride.",
                )
            else:
                try:
                    with transaction.atomic():
                        assignment.save()
                        ride.driver = assignment.driver
                        ride.status = Ride.Status.DRIVER_ASSIGNED
                        ride.save(
                            update_fields=[
                                "driver",
                                "status",
                                "updated_at",
                            ]
                        )
                    messages.success(
                        request,
                        f"Driver {assignment.driver.driver_code} assigned to {ride.ride_number}.",
                    )
                    return redirect(
                        "ride_details",
                        pk=ride.pk,
                    )
                except Exception:
                    messages.error(
                        request,
                        "Unable to assign driver. Please try again.",
                    )
    else:
        form = RideDriverAssignmentForm(
            initial={
                "ride": ride,
                "status": RideDriverAssignment.Status.ASSIGNED,
            }
        )
    form.fields["ride"].queryset = Ride.objects.filter(
        pk=ride.pk
    )
    context = {
        "form": form,
        "ride": ride,
        "page_title": "Assign Driver",
        "is_edit": False,
    }
    return render(
        request,
        "rides/assignment_form.html",
        context,
    )
@login_required
def ride_assignment_edit(request, pk):
    assignment = get_object_or_404(
        RideDriverAssignment.objects
        .select_related(
            "ride",
            "driver",
            "driver__user",
        ),
        pk=pk,
    )
    ride = assignment.ride
    if ride.status in [
        Ride.Status.COMPLETED,
        Ride.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "Assignment cannot be changed for a completed or cancelled ride.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if request.method == "POST":
        form = RideDriverAssignmentForm(
            request.POST,
            instance=assignment,
        )
        if form.is_valid():
            new_assignment = form.save(
                commit=False
            )
            new_assignment.ride = ride
            duplicate = (
                RideDriverAssignment.objects
                .filter(
                    ride=ride,
                    driver=new_assignment.driver,
                    status__in=[
                        RideDriverAssignment.Status.ASSIGNED,
                        RideDriverAssignment.Status.ACCEPTED,
                    ],
                )
                .exclude(
                    pk=assignment.pk
                )
                .exists()
            )
            if duplicate:
                form.add_error(
                    "driver",
                    "This driver is already actively assigned to this ride.",
                )
            else:
                try:
                    with transaction.atomic():
                        assignment = form.save()
                        if assignment.status in [
                            RideDriverAssignment.Status.ASSIGNED,
                            RideDriverAssignment.Status.ACCEPTED,
                        ]:
                            ride.driver = assignment.driver
                            ride.status = Ride.Status.DRIVER_ASSIGNED
                            ride.save(
                                update_fields=[
                                    "driver",
                                    "status",
                                    "updated_at",
                                ]
                            )
                    messages.success(
                        request,
                        "Driver assignment updated successfully.",
                    )
                    return redirect(
                        "ride_details",
                        pk=ride.pk,
                    )
                except Exception:
                    messages.error(
                        request,
                        "Unable to update driver assignment.",
                    )
    else:
        form = RideDriverAssignmentForm(
            instance=assignment
        )
    form.fields["ride"].queryset = Ride.objects.filter(
        pk=ride.pk
    )
    context = {
        "form": form,
        "assignment": assignment,
        "ride": ride,
        "page_title": "Edit Driver Assignment",
        "is_edit": True,
    }
    return render(
        request,
        "rides/assignment_form.html",
        context,
    )
@login_required
def ride_assignment_delete(request, pk):
    assignment = get_object_or_404(
        RideDriverAssignment.objects
        .select_related(
            "ride",
            "driver",
        ),
        pk=pk,
    )
    ride = assignment.ride
    if request.method != "POST":
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if ride.status in [
        Ride.Status.COMPLETED,
        Ride.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "Assignment cannot be removed from a completed or cancelled ride.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    try:
        with transaction.atomic():
            was_current_driver = (
                ride.driver_id == assignment.driver_id
            )
            assignment.delete()
            if was_current_driver:
                next_assignment = (
                    ride.driver_assignments
                    .filter(
                        status__in=[
                            RideDriverAssignment.Status.ASSIGNED,
                            RideDriverAssignment.Status.ACCEPTED,
                        ]
                    )
                    .select_related(
                        "driver"
                    )
                    .order_by(
                        "-assigned_at"
                    )
                    .first()
                )
                if next_assignment:
                    ride.driver = next_assignment.driver
                    ride.save(
                        update_fields=[
                            "driver",
                            "updated_at",
                        ]
                    )
        messages.success(
            request,
            "Driver assignment removed successfully.",
        )
    except ProtectedError:
        messages.error(
            request,
            "This driver assignment cannot be deleted.",
        )
    return redirect(
        "ride_details",
        pk=ride.pk,
    )
@login_required
def ride_tracking_create(request, ride_pk):
    ride = get_object_or_404(
        Ride.objects
        .select_related(
            "driver",
            "driver__user",
        ),
        pk=ride_pk,
    )
    if ride.status in [
        Ride.Status.COMPLETED,
        Ride.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "Tracking cannot be added to a completed or cancelled ride.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if not ride.driver_id:
        messages.warning(
            request,
            "Tracking cannot be added because this ride has no driver assigned.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
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
            if tracking.driver_id != ride.driver_id:
                form.add_error(
                    "driver",
                    "Tracking driver must match the ride driver.",
                )
            else:
                try:
                    tracking.save()
                    messages.success(
                        request,
                        "Ride tracking location added successfully.",
                    )
                    return redirect(
                        "ride_details",
                        pk=ride.pk,
                    )
                except Exception:
                    messages.error(
                        request,
                        "Unable to save tracking information.",
                    )
    else:
        form = RideTrackingForm(
            initial={
                "ride": ride,
                "driver": ride.driver,
            }
        )
    form.fields["ride"].queryset = Ride.objects.filter(
        pk=ride.pk
    )
    form.fields["driver"].queryset = form.fields[
        "driver"
    ].queryset.filter(
        pk=ride.driver_id
    )
    latest_tracking = (
        ride.tracking_points
        .order_by(
            "-recorded_at"
        )
        .first()
    )
    context = {
        "form": form,
        "ride": ride,
        "latest_tracking": latest_tracking,
        "page_title": "Add Ride Tracking",
        "submit_text": "Save Tracking Point",
    }
    return render(
        request,
        "rides/tracking_form.html",
        context,
    )
@login_required
def ride_tracking_list(request, ride_pk):
    ride = get_object_or_404(
        Ride.objects
        .select_related(
            "passenger",
            "driver",
            "driver__user",
            "vehicle",
            "vehicle__vehicle_type",
            "pickup_location",
            "drop_location",
        ),
        pk=ride_pk,
    )
    tracking_points = (
        ride.tracking_points
        .select_related(
            "driver",
        )
        .order_by(
            "-recorded_at"
        )
    )
    latest_tracking = tracking_points.first()
    page_obj = _paginate(
        tracking_points,
        request,
        per_page=20,
    )
    context = {
        "ride": ride,
        "tracking_points": page_obj.object_list,
        "page_obj": page_obj,
        "latest_tracking": latest_tracking,
    }
    return render(
        request,
        "rides/ride_tracking_list.html",
        context,
    )
@login_required
def ride_tracking_delete(request, pk):
    tracking = get_object_or_404(
        RideTracking.objects.select_related(
            "ride",
            "driver",
        ),
        pk=pk,
    )
    ride = tracking.ride
    if request.method == "POST":
        if ride.status in [
            Ride.Status.COMPLETED,
            Ride.Status.CANCELLED,
        ]:
            messages.warning(
                request,
                "Tracking points cannot be deleted from a completed or cancelled ride.",
            )
            return redirect(
                "ride_tracking_list",
                ride_pk=ride.pk,
            )
        try:
            tracking.delete()
            messages.success(
                request,
                "Tracking point deleted successfully.",
            )
        except ProtectedError:
            messages.error(
                request,
                "This tracking point cannot be deleted.",
            )
        return redirect(
            "ride_tracking_list",
            ride_pk=ride.pk,
        )
    context = {
        "tracking": tracking,
        "ride": ride,
    }
    return render(
        request,
        "rides/ride_tracking_delete.html",
        context,
    )
@login_required
def ride_cancellation_create(request, ride_pk):
    ride = get_object_or_404(
        Ride.objects.select_related(
            "ride_request",
            "passenger",
            "driver",
        ),
        pk=ride_pk,
    )
    if ride.status == Ride.Status.COMPLETED:
        messages.warning(
            request,
            "A completed ride cannot be cancelled.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if ride.status == Ride.Status.CANCELLED:
        messages.info(
            request,
            "This ride is already cancelled.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    if hasattr(ride, "cancellation"):
        messages.info(
            request,
            "Cancellation record already exists for this ride.",
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
            cancellation = form.save(
                commit=False
            )
            cancellation.ride = ride
            cancellation.cancelled_by = request.user
            reason = cancellation.reason
            if reason.charge_applicable:
                cancellation.cancellation_charge = reason.charge_amount
            else:
                cancellation.cancellation_charge = 0
            try:
                with transaction.atomic():
                    cancellation.save()
                    ride.status = Ride.Status.CANCELLED
                    ride.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )
                    if ride.ride_request:
                        ride_request = ride.ride_request
                        if ride_request.status not in [
                            RideRequest.Status.COMPLETED,
                            RideRequest.Status.CANCELLED,
                        ]:
                            ride_request.status = RideRequest.Status.CANCELLED
                            ride_request.save(
                                update_fields=[
                                    "status",
                                    "updated_at",
                                ]
                            )
                messages.success(
                    request,
                    f"Ride {ride.ride_number} cancelled successfully.",
                )
                return redirect(
                    "ride_details",
                    pk=ride.pk,
                )
            except ProtectedError:
                messages.error(
                    request,
                    "Cancellation could not be saved because a related record is protected.",
                )
            except Exception:
                messages.error(
                    request,
                    "Unable to cancel this ride. Please try again.",
                )
    else:
        form = RideCancellationForm(
            initial={
                "ride": ride,
                "cancelled_by": request.user,
                "cancellation_charge": 0,
            }
        )
    form.fields["ride"].queryset = Ride.objects.filter(
        pk=ride.pk
    )
    if "cancelled_by" in form.fields:
        form.fields["cancelled_by"].queryset = (
            form.fields["cancelled_by"].queryset.filter(
                pk=request.user.pk
            )
        )
    context = {
        "form": form,
        "ride": ride,
        "page_title": "Cancel Ride",
    }
    return render(
        request,
        "rides/cancellation_form.html",
        context,
    )
@login_required
def ride_rating_create(request, ride_pk):
    ride = get_object_or_404(
        Ride.objects.select_related(
            "passenger",
            "driver",
            "driver__user",
        ),
        pk=ride_pk,
    )
    if ride.status != Ride.Status.COMPLETED:
        messages.warning(
            request,
            "A rating can only be added after ride completion.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
        )
    participant_ids = {
        ride.passenger_id,
        ride.driver.user_id,
    }
    if request.method == "POST":
        form = RideRatingForm(
            request.POST
        )
        if form.is_valid():
            rating = form.save(
                commit=False
            )
            rating.ride = ride
            if rating.from_user_id not in participant_ids:
                form.add_error(
                    "from_user",
                    "Only the passenger or driver of this ride can give a rating.",
                )
            if rating.to_user_id not in participant_ids:
                form.add_error(
                    "to_user",
                    "Rating can only be given to the passenger or driver of this ride.",
                )
            if (
                rating.from_user_id
                and rating.to_user_id
                and rating.from_user_id == rating.to_user_id
            ):
                form.add_error(
                    "to_user",
                    "A user cannot rate themselves.",
                )
            if (
                rating.from_user_id
                and rating.to_user_id
                and rating.from_user_id in participant_ids
                and rating.to_user_id in participant_ids
            ):
                duplicate = RideRating.objects.filter(
                    ride=ride,
                    from_user_id=rating.from_user_id,
                    to_user_id=rating.to_user_id,
                ).exists()
                if duplicate:
                    form.add_error(
                        "rating",
                        "You have already submitted this rating.",
                    )
            if not form.errors:
                try:
                    rating.save()
                    messages.success(
                        request,
                        "Ride rating submitted successfully.",
                    )
                    return redirect(
                        "ride_details",
                        pk=ride.pk,
                    )
                except Exception:
                    messages.error(
                        request,
                        "Unable to save the rating. Please try again.",
                    )
    else:
        form = RideRatingForm(
            initial={
                "ride": ride,
                "from_user": request.user,
            }
        )
    form.fields["ride"].queryset = Ride.objects.filter(
        pk=ride.pk
    )
    form.fields["from_user"].queryset = (
        form.fields["from_user"].queryset.filter(
            pk__in=participant_ids
        )
    )
    form.fields["to_user"].queryset = (
        form.fields["to_user"].queryset.filter(
            pk__in=participant_ids
        )
    )
    context = {
        "form": form,
        "ride": ride,
        "page_title": "Add Ride Rating",
        "submit_text": "Submit Rating",
    }
    return render(
        request,
        "rides/rating_form.html",
        context,
    )
@login_required
def ride_stop_list(request, ride_pk):
    ride = get_object_or_404(
        Ride.objects
        .select_related(
            "passenger",
            "driver",
            "driver__user",
            "vehicle",
            "vehicle__vehicle_type",
            "pickup_location",
            "drop_location",
        ),
        pk=ride_pk,
    )
    stops = (
        ride.stops
        .select_related(
            "location",
        )
        .order_by(
            "stop_order"
        )
    )
    return render(
        request,
        "rides/ride_stop_list.html",
        {
            "ride": ride,
            "stops": stops,
        },
    )
@login_required
def ride_stop_create(request, ride_pk):
    ride = get_object_or_404(
        Ride,
        pk=ride_pk,
    )
    if ride.status in [
        Ride.Status.COMPLETED,
        Ride.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "Stops cannot be added to a completed or cancelled ride.",
        )
        return redirect(
            "ride_details",
            pk=ride.pk,
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
        form = RideStopForm(
            initial={
                "ride": ride,
                "stop_order": ride.stops.count() + 1,
            }
        )
    form.fields["ride"].queryset = Ride.objects.filter(
        pk=ride.pk
    )
    context = {
        "form": form,
        "ride": ride,
        "page_title": "Add Ride Stop",
        "submit_text": "Add Stop",
        "is_edit": False,
    }
    return render(
        request,
        "rides/ride_stop_form.html",
        context,
    )
@login_required
def ride_stop_edit(request, pk):
    stop = get_object_or_404(
        RideStop.objects
        .select_related(
            "ride",
            "location",
        ),
        pk=pk,
    )
    ride = stop.ride
    if ride.status in [
        Ride.Status.COMPLETED,
        Ride.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "Stops cannot be changed for a completed or cancelled ride.",
        )
        return redirect(
            "ride_stop_list",
            ride_pk=ride.pk,
        )
    if request.method == "POST":
        form = RideStopForm(
            request.POST,
            instance=stop,
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Ride stop updated successfully.",
            )
            return redirect(
                "ride_stop_list",
                ride_pk=ride.pk,
            )
    else:
        form = RideStopForm(
            instance=stop
        )
    form.fields["ride"].queryset = Ride.objects.filter(
        pk=ride.pk
    )
    context = {
        "form": form,
        "ride": ride,
        "stop": stop,
        "page_title": "Edit Ride Stop",
        "submit_text": "Update Stop",
        "is_edit": True,
    }
    return render(
        request,
        "rides/ride_stop_form.html",
        context,
    )
@login_required
def ride_stop_delete(request, pk):
    stop = get_object_or_404(
        RideStop.objects
        .select_related(
            "ride",
            "location",
        ),
        pk=pk,
    )
    ride_pk = stop.ride.pk
    if request.method != "POST":
        return redirect(
            "ride_stop_list",
            ride_pk=ride_pk,
        )
    if stop.ride.status in [
        Ride.Status.COMPLETED,
        Ride.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "Stops cannot be deleted from a completed or cancelled ride.",
        )
        return redirect(
            "ride_stop_list",
            ride_pk=ride_pk,
        )
    try:
        stop.delete()
        messages.success(
            request,
            "Ride stop deleted successfully.",
        )
    except ProtectedError:
        messages.error(
            request,
            "This ride stop cannot be deleted.",
        )
    return redirect(
        "ride_stop_list",
        ride_pk=ride_pk,
    )