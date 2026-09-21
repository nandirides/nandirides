from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CouponForm
from .models import Coupon, CouponUsage


@login_required
@permission_required("promotions.view_coupon", raise_exception=True)
def promotions_dashboard(request):
    total_coupons = Coupon.objects.count()
    active_coupons = Coupon.objects.filter(
        is_active=True
    ).count()
    inactive_coupons = Coupon.objects.filter(
        is_active=False
    ).count()
    total_usages = CouponUsage.objects.count()
    total_discount = (
        CouponUsage.objects.aggregate(
            total=Sum("discount_amount")
        )["total"]
        or 0
    )

    context = {
        "page_title": "Promotions Dashboard",
        "breadcrumb_items": [
            {
                "title": "Promotions Dashboard",
                "url": "promotions_dashboard",
            },
        ],
        "total_coupons": total_coupons,
        "active_coupons": active_coupons,
        "inactive_coupons": inactive_coupons,
        "total_usages": total_usages,
        "total_discount": total_discount,
    }

    return render(
        request,
        "promotions/promotions_dashboard.html",
        context,
    )


@login_required
@permission_required("promotions.view_coupon", raise_exception=True)
def coupon_list(request):
    coupons = Coupon.objects.all().order_by("-id")

    context = {
        "coupons": coupons,
        "page_title": "Coupons",
        "breadcrumb_items": [
            {
                "title": "Coupons",
                "url": "coupon_list",
            },
        ],
        "total_coupons": coupons.count(),
        "active_coupons": coupons.filter(
            is_active=True
        ).count(),
        "inactive_coupons": coupons.filter(
            is_active=False
        ).count(),
    }

    return render(
        request,
        "promotions/coupon_list.html",
        context,
    )


@login_required
@permission_required("promotions.add_coupon", raise_exception=True)
def coupon_create(request):
    if request.method == "POST":
        form = CouponForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                coupon = form.save()

            messages.success(
                request,
                f"Coupon {coupon.code} created successfully.",
            )

            return redirect(
                "coupon_detail",
                pk=coupon.pk,
            )
    else:
        form = CouponForm()

    context = {
        "form": form,
        "page_title": "Add Coupon",
        "breadcrumb_items": [
            {
                "title": "Add Coupon",
                "url": "coupon_create",
            },
        ],
        "form_title": "Create Coupon",
    }

    return render(
        request,
        "promotions/coupon_form.html",
        context,
    )


@login_required
@permission_required("promotions.change_coupon", raise_exception=True)
def coupon_edit(request, pk):
    coupon = get_object_or_404(
        Coupon,
        pk=pk,
    )

    if request.method == "POST":
        form = CouponForm(
            request.POST,
            instance=coupon,
        )

        if form.is_valid():
            with transaction.atomic():
                coupon = form.save()

            messages.success(
                request,
                f"Coupon {coupon.code} updated successfully.",
            )

            return redirect(
                "coupon_detail",
                pk=coupon.pk,
            )
    else:
        form = CouponForm(
            instance=coupon,
        )

    context = {
        "form": form,
        "coupon": coupon,
        "page_title": "Edit Coupon",
        "breadcrumb_items": [
            {
                "title": "Edit Coupon",
                "url": "coupon_edit", 
            },
        ],
        "form_title": "Update Coupon",
    }

    return render(
        request,
        "promotions/coupon_form.html",
        context,
    )


@login_required
@permission_required("promotions.view_coupon", raise_exception=True)
def coupon_detail(request, pk):
    coupon = get_object_or_404(
        Coupon,
        pk=pk,
    )

    usage_count = coupon.usages.count()

    context = {
        "coupon": coupon,
        "usage_count": usage_count,
        "page_title": "Coupon Details",
        "breadcrumb_items": [
            {
                "title": "Coupon Details",
                "url": "coupon_detail", 
            },
        ],
    }

    return render(
        request,
        "promotions/coupon_detail.html",
        context,
    )


@login_required
@permission_required("promotions.change_coupon", raise_exception=True)
def coupon_toggle(request, pk):
    if request.method != "POST":
        return redirect(
            "coupon_detail",
            pk=pk,
        )

    coupon = get_object_or_404(
        Coupon,
        pk=pk,
    )

    coupon.is_active = not coupon.is_active

    coupon.save(
        update_fields=[
            "is_active",
        ]
    )

    messages.success(
        request,
        (
            f"Coupon {coupon.code} activated successfully."
            if coupon.is_active
            else f"Coupon {coupon.code} deactivated successfully."
        ),
    )

    return redirect(
        "coupon_detail",
        pk=coupon.pk,
    )


@login_required
@permission_required("promotions.view_couponusage", raise_exception=True)
def coupon_usage_list(request):
    usages = (
        CouponUsage.objects.select_related(
            "coupon",
            "user",
            "ride",
        )
        .all()
        .order_by("-id")
    )

    total_discount = (
        usages.aggregate(
            total=Sum("discount_amount")
        )["total"]
        or 0
    )

    context = {
        "usages": usages,
        "page_title": "Coupon Usage",
        "breadcrumb_items": [
            {
                "title": "Coupon Usage",
                "url": "coupon_usage_list", 
            },
        ],
        "total_usages": usages.count(),
        "total_discount": total_discount,
    }

    return render(
        request,
        "promotions/coupon_usage_list.html",
        context,
    )


@login_required
@permission_required("promotions.view_couponusage", raise_exception=True)
def coupon_usage_detail(request, pk):
    usage = get_object_or_404(
        CouponUsage.objects.select_related(
            "coupon",
            "user",
            "ride",
        ),
        pk=pk,
    )

    context = {
        "usage": usage,
        "page_title": "Coupon Usage Details",
        "breadcrumb_items": [
            {
                "title": "Coupon Usage Details",
                "url": "coupon_usage_detail", 
            },
        ],
    }

    return render(
        request,
        "promotions/coupon_usage_detail.html",
        context,
    )