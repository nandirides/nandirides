from datetime import timedelta
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Count
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import VehicleTypeForm, VehicleForm, DriverVehicleForm, VehicleDocumentForm
from .models import VehicleType, Vehicle, DriverVehicle, VehicleDocument
from django.urls import reverse

def vehicle_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
            if request.user.is_superuser or request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator

@login_required
@vehicle_permission("vehicle.view_vehicle")
def vehicle_dashboard(request):
    today = timezone.localdate()
    expiry_warning_date = today + timedelta(days=30)
    vehicles = Vehicle.objects.select_related("vehicle_type")
    total_vehicles = vehicles.count()
    active_vehicles = vehicles.filter(status=Vehicle.Status.ACTIVE).count()
    inactive_vehicles = vehicles.filter(status=Vehicle.Status.INACTIVE).count()
    maintenance_vehicles = vehicles.filter(status=Vehicle.Status.MAINTENANCE).count()
    blocked_vehicles = vehicles.filter(status=Vehicle.Status.BLOCKED).count()
    current_assignments = (
        DriverVehicle.objects
        .filter(is_current=True)
        .select_related(
            "driver",
            "driver__user",
            "vehicle",
            "vehicle__vehicle_type",
        )
    )
    assigned_vehicle_ids = current_assignments.values_list(
        "vehicle_id",
        flat=True,
    )
    assigned_vehicles = current_assignments.count()
    unassigned_vehicles = (
        vehicles
        .filter(status=Vehicle.Status.ACTIVE)
        .exclude(pk__in=assigned_vehicle_ids)
        .count()
    )
    expired_documents = VehicleDocument.objects.filter(
        expiry_date__lt=today
    ).count()
    expiring_documents = VehicleDocument.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=expiry_warning_date,
    ).count()
    recent_vehicles = vehicles.order_by("-created_at")[:8]
    recent_assignments = current_assignments.order_by(
        "-assigned_from"
    )[:8]
    expiring_document_list = (
        VehicleDocument.objects
        .filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=expiry_warning_date,
        )
        .select_related(
            "vehicle",
            "vehicle__vehicle_type",
        )
        .order_by("expiry_date")[:8]
    )
    context = {
        "page_title": "Vehicle Dashboard",
        "breadcrumb_items": [
            {
                "title": "Vehicle Dashboard",
                "url": reverse("vehicle_dashboard"),
            },
        ],
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "inactive_vehicles": inactive_vehicles,
        "maintenance_vehicles": maintenance_vehicles,
        "blocked_vehicles": blocked_vehicles,
        "assigned_vehicles": assigned_vehicles,
        "unassigned_vehicles": unassigned_vehicles,
        "expired_documents": expired_documents,
        "expiring_documents": expiring_documents,
        "recent_vehicles": recent_vehicles,
        "recent_assignments": recent_assignments,
        "expiring_document_list": expiring_document_list,
        "today": today,
        "expiry_warning_date": expiry_warning_date,
    }
    return render(
        request,
        "vehicle/vehicle_dashboard.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.view_vehicletype")
def vehicle_type_list(request):
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    vehicle_types = (
        VehicleType.objects
        .annotate(vehicle_count=Count("vehicles"))
        .order_by("name")
    )
    if search:
        vehicle_types = vehicle_types.filter(
            Q(name__icontains=search)
            | Q(code__icontains=search)
            | Q(description__icontains=search)
        )
    if status == "active":
        vehicle_types = vehicle_types.filter(is_active=True)
    elif status == "inactive":
        vehicle_types = vehicle_types.filter(is_active=False)
    else:
        status = ""
    context = {
        "page_title": "Vehicle Types",
        "breadcrumb_items": [
            {
                "title": "Vehicle Types",
                "url": reverse("vehicle_type_list"),
            },
        ],
        "vehicle_types": vehicle_types,
        "search": search,
        "selected_status": status,
    }
    return render(
        request,
        "vehicle/vehicle_type_list.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.add_vehicletype")
def vehicle_type_form(request, pk=None):
    vehicle_type = (
        get_object_or_404(VehicleType, pk=pk)
        if pk
        else None
    )
    if (
        vehicle_type
        and not request.user.is_superuser
        and not request.user.has_perm("vehicle.change_vehicletype")
    ):
        raise PermissionDenied
    if request.method == "POST":
        form = VehicleTypeForm(
            request.POST,
            instance=vehicle_type,
        )
        if form.is_valid():
            vehicle_type = form.save()
            action = "updated" if pk else "created"
            messages.success(
                request,
                f"Vehicle type '{vehicle_type.name}' {action} successfully.",
            )
            return redirect("vehicle_type_list")
    else:
        form = VehicleTypeForm(
            instance=vehicle_type
        )
    context = {
        "page_title": (
            "Edit Vehicle Type"
            if vehicle_type
            else "Add Vehicle Type"
        ),
        "breadcrumb_items": [
            {
                "title": "Vehicle Types",
                "url": reverse("vehicle_type_list"),
            },
            {
                "title": (
                    "Edit Vehicle Type"
                    if vehicle_type
                    else "Add Vehicle Type"
                ),
                "url": (
                    reverse("vehicle_type_form_edit", args=[vehicle_type.id])
                    if vehicle_type
                    else reverse("vehicle_type_add")
                ),
            },
        ],
        "form": form,
        "vehicle_type": vehicle_type,
    }
    return render(
        request,
        "vehicle/vehicle_type_form.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.delete_vehicletype")
def vehicle_type_delete(request, pk):
    vehicle_type = get_object_or_404(
        VehicleType,
        pk=pk,
    )
    if request.method != "POST":
        return redirect("vehicle_type_list")
    try:
        name = vehicle_type.name
        with transaction.atomic():
            vehicle_type.delete()
        messages.success(
            request,
            f"Vehicle type '{name}' deleted successfully.",
        )
    except ProtectedError:
        messages.error(
            request,
            "This vehicle type cannot be deleted because vehicles are using it.",
        )
    return redirect("vehicle_type_list")

@login_required
@vehicle_permission("vehicle.view_vehicle")
def vehicle_list(request):
    search = request.GET.get("search", "").strip()
    vehicle_type = request.GET.get("vehicle_type", "").strip()
    fuel_type = request.GET.get("fuel_type", "").strip()
    status = request.GET.get("status", "").strip()
    vehicles = (
        Vehicle.objects
        .select_related("vehicle_type")
        .prefetch_related(
            "driver_assignments__driver",
            "driver_assignments__driver__user",
        )
    )
    if search:
        vehicles = vehicles.filter(
            Q(vehicle_number__icontains=search)
            | Q(brand__icontains=search)
            | Q(model__icontains=search)
            | Q(variant__icontains=search)
            | Q(color__icontains=search)
        )
    if vehicle_type.isdigit():
        vehicles = vehicles.filter(
            vehicle_type_id=vehicle_type
        )
    elif vehicle_type:
        vehicle_type = ""
    valid_fuel_types = {
        value
        for value, label in Vehicle.FuelType.choices
    }
    valid_statuses = {
        value
        for value, label in Vehicle.Status.choices
    }
    if fuel_type in valid_fuel_types:
        vehicles = vehicles.filter(
            fuel_type=fuel_type
        )
    elif fuel_type:
        fuel_type = ""
    if status in valid_statuses:
        vehicles = vehicles.filter(
            status=status
        )
    elif status:
        status = ""
    vehicles = vehicles.order_by("-created_at")
    context = {
        "page_title": "Vehicles",
        "breadcrumb_items": [
            {
                "title": "Vehicles",
                "url": reverse("vehicle_list"),
            },
        ],
        "vehicles": vehicles,
        "vehicle_types": (
            VehicleType.objects
            .filter(is_active=True)
            .order_by("name")
        ),
        "fuel_choices": Vehicle.FuelType.choices,
        "status_choices": Vehicle.Status.choices,
        "search": search,
        "selected_vehicle_type": vehicle_type,
        "selected_fuel_type": fuel_type,
        "selected_status": status,
    }
    return render(
        request,
        "vehicle/vehicle_list.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.add_vehicle")
def vehicle_form(request, pk=None):
    vehicle = (
        get_object_or_404(
            Vehicle.objects.select_related("vehicle_type"),
            pk=pk,
        )
        if pk
        else None
    )
    if (
        vehicle
        and not request.user.is_superuser
        and not request.user.has_perm("vehicle.change_vehicle")
    ):
        raise PermissionDenied
    if request.method == "POST":
        form = VehicleForm(
            request.POST,
            instance=vehicle,
        )
        if form.is_valid():
            vehicle = form.save()
            action = "updated" if pk else "created"
            messages.success(
                request,
                f"Vehicle {vehicle.vehicle_number} {action} successfully.",
            )
            return redirect(
                "vehicle_detail",
                pk=vehicle.pk,
            )
    else:
        form = VehicleForm(
            instance=vehicle
        )
    context = {
        "page_title": (
            "Edit Vehicle"
            if vehicle
            else "Add Vehicle"
        ),
        "breadcrumb_items": [
            {
                "title": "Vehicles",
                "url": reverse("vehicle_list"),
            },
            {
                "title": (
                    "Edit Vehicle"
                    if vehicle
                    else "Add Vehicle"
                ),
                "url": (
                    reverse("vehicle_edit", args=[vehicle.id])
                    if vehicle
                    else reverse("vehicle_add")
                ),
            },
        ],
        "form": form,
        "vehicle": vehicle,
    }
    return render(
        request,
        "vehicle/vehicle_form.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.view_vehicle")
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(
        Vehicle.objects.select_related("vehicle_type"),
        pk=pk,
    )
    current_assignment = (
        DriverVehicle.objects
        .filter(
            vehicle=vehicle,
            is_current=True,
        )
        .select_related(
            "driver",
            "driver__user",
        )
        .first()
    )
    assignment_history = (
        DriverVehicle.objects
        .filter(vehicle=vehicle)
        .select_related(
            "driver",
            "driver__user",
        )
        .order_by("-assigned_from")
    )
    documents = (
        VehicleDocument.objects
        .filter(vehicle=vehicle)
        .order_by(
            "-expiry_date",
            "-created_at",
        )
    )
    context = {
        "page_title": "Vehicle Details",
        "breadcrumb_items": [
            {
                "title": "Vehicle Details",
                "url": reverse("vehicle_detail"),
            },
        ],
        "vehicle": vehicle,
        "current_assignment": current_assignment,
        "assignment_history": assignment_history,
        "assignments": assignment_history,
        "documents": documents,
    }
    return render(
        request,
        "vehicle/vehicle_detail.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.delete_vehicle")
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
    )
    if request.method != "POST":
        return redirect(
            "vehicle_detail",
            pk=pk,
        )
    if DriverVehicle.objects.filter(
        vehicle=vehicle
    ).exists():
        messages.error(
            request,
            "This vehicle cannot be deleted because assignment history exists.",
        )
        return redirect(
            "vehicle_detail",
            pk=pk,
        )
    if VehicleDocument.objects.filter(
        vehicle=vehicle
    ).exists():
        messages.error(
            request,
            "This vehicle cannot be deleted because vehicle documents exist.",
        )
        return redirect(
            "vehicle_detail",
            pk=pk,
        )
    vehicle_number = vehicle.vehicle_number
    try:
        with transaction.atomic():
            vehicle.delete()
        messages.success(
            request,
            f"Vehicle {vehicle_number} deleted successfully.",
        )
        return redirect("vehicle_list")
    except ProtectedError:
        messages.error(
            request,
            "This vehicle cannot be deleted because it is linked with other records.",
        )
        return redirect(
            "vehicle_detail",
            pk=pk,
        )

@login_required
@vehicle_permission("vehicle.view_drivervehicle")
def assignment_list(request):
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    assignments = (
        DriverVehicle.objects
        .select_related(
            "driver",
            "driver__user",
            "vehicle",
            "vehicle__vehicle_type",
        )
    )
    if search:
        assignments = assignments.filter(
            Q(driver__user__first_name__icontains=search)
            | Q(driver__user__last_name__icontains=search)
            | Q(driver__driver_code__icontains=search)
            | Q(vehicle__vehicle_number__icontains=search)
            | Q(vehicle__brand__icontains=search)
            | Q(vehicle__model__icontains=search)
        )
    if status == "current":
        assignments = assignments.filter(
            is_current=True
        )
    elif status == "ended":
        assignments = assignments.filter(
            is_current=False
        )
    else:
        status = ""
    assignments = assignments.order_by(
        "-assigned_from"
    )
    current_count = DriverVehicle.objects.filter(
        is_current=True
    ).count()
    ended_count = DriverVehicle.objects.filter(
        is_current=False
    ).count()
    context = {
        "page_title": "Driver Assignments",
        "breadcrumb_items": [
            {
                "title": "Driver Assignments",
                "url": reverse("assignment_list"),
            },
        ],
        "assignments": assignments,
        "current_count": current_count,
        "ended_count": ended_count,
        "search": search,
        "selected_status": status,
        "selected_current": status,
    }
    return render(
        request,
        "vehicle/assignment_list.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.add_drivervehicle")
def assignment_form(request, pk=None):
    assignment = (
        get_object_or_404(
            DriverVehicle.objects.select_related(
                "driver",
                "driver__user",
                "vehicle",
                "vehicle__vehicle_type",
            ),
            pk=pk,
        )
        if pk
        else None
    )
    if (
        assignment
        and not request.user.is_superuser
        and not request.user.has_perm(
            "vehicle.change_drivervehicle"
        )
    ):
        raise PermissionDenied
    if request.method == "POST":
        form = DriverVehicleForm(
            request.POST,
            instance=assignment,
        )
        if form.is_valid():
            with transaction.atomic():
                assignment = form.save(
                    commit=False
                )
                if assignment.is_current:
                    (
                        DriverVehicle.objects
                        .filter(
                            driver=assignment.driver,
                            is_current=True,
                        )
                        .exclude(pk=assignment.pk)
                        .update(
                            is_current=False,
                            assigned_to=timezone.now(),
                        )
                    )
                    (
                        DriverVehicle.objects
                        .filter(
                            vehicle=assignment.vehicle,
                            is_current=True,
                        )
                        .exclude(pk=assignment.pk)
                        .update(
                            is_current=False,
                            assigned_to=timezone.now(),
                        )
                    )
                    assignment.assigned_to = None
                elif not assignment.assigned_to:
                    assignment.assigned_to = timezone.now()
                assignment.save()
            action = "updated" if pk else "created"
            messages.success(
                request,
                f"Driver and vehicle assignment {action} successfully.",
            )
            return redirect("assignment_list")
    else:
        form = DriverVehicleForm(
            instance=assignment
        )
    context = {
        "page_title": (
            "Edit Assignment"
            if assignment
            else "Assign Driver"
        ),
        "breadcrumb_items": [
            {
                "title": "Assignments",
                "url": reverse("assignment_list"),
            },
            {
                "title": (
                    "Edit Assignment"
                    if assignment
                    else "Assign Driver"
                ),
                "url": (
                    reverse("assignment_edit", args=[assignment.id])
                    if assignment
                    else reverse("assignment_add")
                ),
            },
        ],
        "form": form,
        "assignment": assignment,
    }
    return render(
        request,
        "vehicle/assignment_form.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.change_drivervehicle")
def assignment_end(request, pk):
    assignment = get_object_or_404(
        DriverVehicle,
        pk=pk,
    )
    if request.method == "POST":
        if assignment.is_current:
            assignment.is_current = False
            assignment.assigned_to = timezone.now()
            assignment.save(
                update_fields=[
                    "is_current",
                    "assigned_to",
                    "updated_at",
                ]
            )
            messages.success(
                request,
                "Vehicle assignment ended successfully.",
            )
        else:
            messages.info(
                request,
                "This assignment has already ended.",
            )
    return redirect("assignment_list")

@login_required
@vehicle_permission("vehicle.view_vehicledocument")
def document_list(request):
    today = timezone.localdate()
    expiry_warning_date = today + timedelta(days=30)
    search = request.GET.get("search", "").strip()
    document_type = request.GET.get(
        "document_type",
        "",
    ).strip()
    verification_status = request.GET.get(
        "verification_status",
        "",
    ).strip()
    expiry = request.GET.get(
        "expiry",
        "",
    ).strip()
    documents = (
        VehicleDocument.objects
        .select_related(
            "vehicle",
            "vehicle__vehicle_type",
        )
    )
    if search:
        documents = documents.filter(
            Q(vehicle__vehicle_number__icontains=search)
            | Q(document_number__icontains=search)
        )
    valid_document_types = {
        value
        for value, label in VehicleDocument.DocumentType.choices
    }
    valid_verification_statuses = {
        "pending",
        "verified",
        "rejected",
    }
    if document_type in valid_document_types:
        documents = documents.filter(
            document_type=document_type
        )
    elif document_type:
        document_type = ""
    if verification_status in valid_verification_statuses:
        documents = documents.filter(
            verification_status=verification_status
        )
    elif verification_status:
        verification_status = ""
    if expiry == "expired":
        documents = documents.filter(
            expiry_date__lt=today
        )
    elif expiry == "30":
        documents = documents.filter(
            expiry_date__gte=today,
            expiry_date__lte=expiry_warning_date,
        )
    elif expiry == "valid":
        documents = documents.filter(
            Q(expiry_date__isnull=True)
            | Q(expiry_date__gt=expiry_warning_date)
        )
    elif expiry:
        expiry = ""
    total_documents = VehicleDocument.objects.count()
    verified_documents = VehicleDocument.objects.filter(
        verification_status="verified"
    ).count()
    pending_documents = VehicleDocument.objects.filter(
        verification_status="pending"
    ).count()
    expired_documents = VehicleDocument.objects.filter(
        expiry_date__lt=today
    ).count()
    documents = documents.order_by(
        "expiry_date",
        "-created_at",
    )
    context = {
        "page_title": "Vehicle Documents",
        "breadcrumb_items": [
            {
                "title": "Vehicle Documents",
                "url": reverse("document_list"),
            },
        ],
        "documents": documents,
        "total_documents": total_documents,
        "verified_documents": verified_documents,
        "pending_documents": pending_documents,
        "expired_documents": expired_documents,
        "document_type_choices": VehicleDocument.DocumentType.choices,
        "verification_choices": [
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        "search": search,
        "selected_document_type": document_type,
        "selected_verification_status": verification_status,
        "selected_expiry": expiry,
        "today": today,
        "expiry_warning_date": expiry_warning_date,
    }
    return render(
        request,
        "vehicle/document_list.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.add_vehicledocument")
def document_form(request, pk=None):
    document = (
        get_object_or_404(
            VehicleDocument.objects.select_related(
                "vehicle",
                "vehicle__vehicle_type",
            ),
            pk=pk,
        )
        if pk
        else None
    )
    if (
        document
        and not request.user.is_superuser
        and not request.user.has_perm(
            "vehicle.change_vehicledocument"
        )
    ):
        raise PermissionDenied
    if request.method == "POST":
        form = VehicleDocumentForm(
            request.POST,
            request.FILES,
            instance=document,
        )
        if form.is_valid():
            document = form.save()
            action = "updated" if pk else "uploaded"
            messages.success(
                request,
                f"Vehicle document {action} successfully.",
            )
            return redirect("document_list")
    else:
        form = VehicleDocumentForm(
            instance=document
        )
    context = {
        "page_title": (
            "Edit Vehicle Document"
            if document
            else "Upload Vehicle Document"
        ),
        "breadcrumb_items": [
            {
                "title": "Documents",
                "url": reverse("document_list"),
            },
            {
                "title": (
                    "Edit Vehicle Document"
                    if document
                    else "Upload Vehicle Document"
                ),
                "url": (
                    reverse("document_edit", args=[document.id])
                    if document
                    else reverse("document_add")
                ),
            },
        ],
        "form": form,
        "document": document,
    }
    return render(
        request,
        "vehicle/document_form.html",
        context,
    )

@login_required
@vehicle_permission("vehicle.delete_vehicledocument")
def document_delete(request, pk):
    document = get_object_or_404(
        VehicleDocument,
        pk=pk,
    )
    if request.method != "POST":
        return redirect("document_list")
    try:
        document.delete()
        messages.success(
            request,
            "Vehicle document deleted successfully.",
        )
    except ProtectedError:
        messages.error(
            request,
            "This vehicle document cannot be deleted because it is linked with another record.",
        )
    return redirect("document_list")
