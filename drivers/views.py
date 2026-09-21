from django.contrib import messages
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from .forms import DriverDocumentForm, DriverForm
from .models import Driver, DriverDocument
from django.urls import reverse

def driver_list(request):
    drivers = Driver.objects.select_related("user").all().order_by("-id")
    context = {
        "page_title": "Drivers",
        "breadcrumb_items": [
            {
                "title": "Drivers",
                "url": "driver_list"
            },
        ],
        "drivers": drivers,
        "total_drivers": drivers.count(),
        "active_drivers": drivers.filter(
            status=Driver.Status.ACTIVE
        ).count(),
        "pending_drivers": drivers.filter(
            status=Driver.Status.PENDING
        ).count(),
        "verified_drivers": drivers.filter(
            verification_status=Driver.VerificationStatus.VERIFIED
        ).count(),
    }
    return render(
        request,
        "driver/driver_list.html",
        context
    )

def driver_form(request, pk=None):
    driver = None
    if pk:
        driver = get_object_or_404(
            Driver.objects.select_related("user"),
            pk=pk
        )
    if request.method == "POST":
        form = DriverForm(
            request.POST,
            instance=driver
        )
        if form.is_valid():
            with transaction.atomic():
                driver = form.save()
            if pk:
                messages.success(
                    request,
                    f"Driver {driver.driver_code} updated successfully."
                )
            else:
                messages.success(
                    request,
                    f"Driver {driver.driver_code} created successfully."
                )
            return redirect("driver_list")
    else:
        form = DriverForm(
            instance=driver
        )
    context = {
        "form": form,
        "driver": driver,
        "page_title": "Edit Driver" if pk else "Add Driver",
        "breadcrumb_items": [
            {
                "title": "Edit Driver" if pk else "Add Driver",
                "url": (
                    reverse("driver_edit", args=[pk])
                    if pk
                    else reverse("driver_create")
                ),
            },
        ],
    }
    return render(
        request,
        "driver/driver_form.html",
        context
    )

def driver_detail(request, pk):
    driver = get_object_or_404(
        Driver.objects.select_related("user"),
        pk=pk
    )
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete_driver":
            driver_code = driver.driver_code
            try:
                with transaction.atomic():
                    driver.delete()
                messages.success(
                    request,
                    f"Driver {driver_code} deleted successfully."
                )
                return redirect("driver_list")
            except ProtectedError:
                messages.error(
                    request,
                    f"Driver {driver_code} cannot be deleted because related earning or payout records exist."
                )
                return redirect(
                    "driver_detail",
                    pk=driver.pk
                )
    documents = driver.documents.select_related(
        "verified_by"
    ).all().order_by("-id")
    bank_accounts = driver.bank_accounts.all().order_by(
        "-is_primary",
        "-id"
    )
    earnings = driver.earnings.select_related(
        "ride"
    ).all().order_by("-id")
    payouts = driver.payouts.all().order_by("-id")
    context = {
        "driver": driver,
        "documents": documents,
        "bank_accounts": bank_accounts,
        "earnings": earnings,
        "payouts": payouts,
        "page_title": "Driver Details",
        "breadcrumb_items": [
            {
                "title": "Driver Details",
                "url": "driver_detail"
            },
        ],
    }
    return render(
        request,
        "driver/driver_detail.html",
        context
    )

def driver_document_form(request, driver_pk, pk=None):
    driver = get_object_or_404(
        Driver,
        pk=driver_pk
    )
    document = None
    if pk:
        document = get_object_or_404(
            DriverDocument,
            pk=pk,
            driver=driver
        )
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete_document" and document:
            document_name = document.get_document_type_display()
            document_file = document.document_file
            with transaction.atomic():
                document.delete()
            if document_file:
                document_file.delete(save=False)
            messages.success(
                request,
                f"{document_name} deleted successfully."
            )
            return redirect(
                "driver_detail",
                pk=driver.pk
            )
        form = DriverDocumentForm(
            request.POST,
            request.FILES,
            instance=document
        )
        if form.is_valid():
            with transaction.atomic():
                document = form.save(commit=False)
                document.driver = driver
                document.save()
            if pk:
                messages.success(
                    request,
                    "Driver document updated successfully."
                )
            else:
                messages.success(
                    request,
                    "Driver document added successfully."
                )
            return redirect(
                "driver_detail",
                pk=driver.pk
            )
    else:
        form = DriverDocumentForm(
            instance=document
        )
    context = {
        "form": form,
        "driver": driver,
        "document": document,
        "page_title": "Edit Document" if pk else "Add Document",
        "breadcrumb_items": [
            {
                "title": "Edit Document" if pk else "Add Document",
                "url": (
                    reverse("ddriver_document_edit", args=[pk])
                    if pk
                    else reverse("driver_document_create")
                ),
            },
        ],
    }
    return render(
        request,
        "driver/driver_document_form.html",
        context
    )