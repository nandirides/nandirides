from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RefundForm
from .models import Payment, Refund
from django.urls import reverse

def payment_list(request):
    payments = Payment.objects.select_related(
        "user",
        "ride",
    ).prefetch_related(
        "refunds",
    ).all().order_by("-id")
    context = {
        "payments": payments,
        "page_title": "Payments",
        "breadcrumb_items": [
            {
                "title": "Payments",
                "url": "payment_list"
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
        ).prefetch_related(
            "refunds",
        ),
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
                "url": "payment_detail"
            },
        ],
    }
    return render(
        request,
        "payment/payment_detail.html",
        context,
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
                refund = form.save(commit=False)
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
        "page_title": "Edit Refund" if pk else "Add Refund",
        "breadcrumb_items": [
            {
                "title": "Refunds",
                "url": reverse("payment_list"),
            },
            {
                "title": "Edit Refund" if pk else "Add Refund",
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