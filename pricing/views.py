from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FareRuleForm, SurgePricingForm
from .models import FareBreakdown, FareRule, SurgePricing


@login_required
@permission_required("pricing.view_farerule", raise_exception=True)
def pricing_dashboard(request):
    total_rules = FareRule.objects.count()
    active_rules = FareRule.objects.filter(is_active=True).count()
    inactive_rules = FareRule.objects.filter(is_active=False).count()
    total_surge = SurgePricing.objects.count()
    active_surge = SurgePricing.objects.filter(is_active=True).count()
    inactive_surge = SurgePricing.objects.filter(is_active=False).count()
    total_breakdowns = FareBreakdown.objects.count()

    context = {
        "page_title": "Pricing Dashboard",
        "breadcrumb_items": [
            {
                "title": "Pricing Dashboard",
                "url": "pricing_dashboard",
            },
        ],
        "total_rules": total_rules,
        "active_rules": active_rules,
        "inactive_rules": inactive_rules,
        "total_surge": total_surge,
        "active_surge": active_surge,
        "inactive_surge": inactive_surge,
        "total_breakdowns": total_breakdowns,
    }

    return render(
        request,
        "pricing/pricing_dashboard.html",
        context,
    )


@login_required
@permission_required("pricing.view_farerule", raise_exception=True)
def fare_rule_list(request):
    fare_rules = (
        FareRule.objects.select_related(
            "city",
            "vehicle_type",
        )
        .all()
        .order_by("-id")
    )

    context = {
        "fare_rules": fare_rules,
        "page_title": "Fare Rules",
        "breadcrumb_items": [
            {
                "title": "Fare Rules",
                "url": "fare_rule_list",
            },
        ],
        "total_rules": fare_rules.count(),
        "active_rules": fare_rules.filter(is_active=True).count(),
        "inactive_rules": fare_rules.filter(is_active=False).count(),
    }

    return render(
        request,
        "pricing/fare_rule_list.html",
        context,
    )


@login_required
@permission_required("pricing.add_farerule", raise_exception=True)
def fare_rule_create(request):
    if request.method == "POST":
        form = FareRuleForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                fare_rule = form.save()

            messages.success(
                request,
                f"Fare rule for {fare_rule.city} - "
                f"{fare_rule.vehicle_type} created successfully.",
            )

            return redirect("fare_rule_list")
    else:
        form = FareRuleForm()

    context = {
        "form": form,
        "page_title": "Add Fare Rule",
        "breadcrumb_items": [
            {
                "title": "Add Fare Rule",
                "url": "fare_rule_create",
            },
        ],
        "form_title": "Create Fare Rule",
    }

    return render(
        request,
        "pricing/fare_rule_form.html",
        context,
    )


@login_required
@permission_required("pricing.change_farerule", raise_exception=True)
def fare_rule_edit(request, pk):
    fare_rule = get_object_or_404(
        FareRule,
        pk=pk,
    )

    if request.method == "POST":
        form = FareRuleForm(
            request.POST,
            instance=fare_rule,
        )

        if form.is_valid():
            with transaction.atomic():
                fare_rule = form.save()

            messages.success(
                request,
                "Fare rule updated successfully.",
            )

            return redirect(
                "fare_rule_detail",
                pk=fare_rule.pk,
            )
    else:
        form = FareRuleForm(
            instance=fare_rule,
        )

    context = {
        "form": form,
        "fare_rule": fare_rule,
        "page_title": "Edit Fare Rule",
        "breadcrumb_items": [
            {
                "title": "Edit Fare Rule",
                "url": "fare_rule_edit",
            },
        ],
        "form_title": "Update Fare Rule",
    }

    return render(
        request,
        "pricing/fare_rule_form.html",
        context,
    )


@login_required
@permission_required("pricing.view_farerule", raise_exception=True)
def fare_rule_detail(request, pk):
    fare_rule = get_object_or_404(
        FareRule.objects.select_related(
            "city",
            "vehicle_type",
        ),
        pk=pk,
    )

    context = {
        "fare_rule": fare_rule,
        "page_title": "Fare Rule Details",
        "breadcrumb_items": [
            {
                "title": "Fare Rule Details",
                "url": "fare_rule_detail",
            },
        ],
    }

    return render(
        request,
        "pricing/fare_rule_detail.html",
        context,
    )


@login_required
@permission_required("pricing.change_farerule", raise_exception=True)
def fare_rule_toggle(request, pk):
    if request.method != "POST":
        return redirect(
            "fare_rule_detail",
            pk=pk,
        )

    fare_rule = get_object_or_404(
        FareRule,
        pk=pk,
    )

    fare_rule.is_active = not fare_rule.is_active

    fare_rule.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if fare_rule.is_active:
        messages.success(
            request,
            "Fare rule activated successfully.",
        )
    else:
        messages.success(
            request,
            "Fare rule deactivated successfully.",
        )

    return redirect(
        "fare_rule_detail",
        pk=fare_rule.pk,
    )


@login_required
@permission_required("pricing.view_surgepricing", raise_exception=True)
def surge_list(request):
    surge_pricing = (
        SurgePricing.objects.select_related(
            "city",
            "vehicle_type",
        )
        .all()
        .order_by("-id")
    )

    context = {
        "surge_pricing": surge_pricing,
        "page_title": "Surge Pricing",
        "breadcrumb_items": [
            {
                "title": "Surge Pricing",
                "url": "surge_list",
            },
        ],
        "total_surge": surge_pricing.count(),
        "active_surge": surge_pricing.filter(is_active=True).count(),
        "inactive_surge": surge_pricing.filter(is_active=False).count(),
    }

    return render(
        request,
        "pricing/surge_list.html",
        context,
    )


@login_required
@permission_required("pricing.add_surgepricing", raise_exception=True)
def surge_create(request):
    if request.method == "POST":
        form = SurgePricingForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                surge = form.save()

            messages.success(
                request,
                "Surge pricing created successfully.",
            )

            return redirect(
                "surge_detail",
                pk=surge.pk,
            )
    else:
        form = SurgePricingForm()

    context = {
        "form": form,
        "page_title": "Add Surge Pricing",
        "breadcrumb_items": [
            {
                "title": "Add Surge Pricing",
                "url": "surge_create",
            },
        ],
        "form_title": "Create Surge Pricing",
    }

    return render(
        request,
        "pricing/surge_form.html",
        context,
    )


@login_required
@permission_required("pricing.change_surgepricing", raise_exception=True)
def surge_edit(request, pk):
    surge = get_object_or_404(
        SurgePricing,
        pk=pk,
    )

    if request.method == "POST":
        form = SurgePricingForm(
            request.POST,
            instance=surge,
        )

        if form.is_valid():
            with transaction.atomic():
                surge = form.save()

            messages.success(
                request,
                "Surge pricing updated successfully.",
            )

            return redirect(
                "surge_detail",
                pk=surge.pk,
            )
    else:
        form = SurgePricingForm(
            instance=surge,
        )

    context = {
        "form": form,
        "surge": surge,
        "page_title": "Edit Surge Pricing",
        "breadcrumb_items": [
            {
                "title": "Edit Surge Pricing",
                "url": "surge_edit",
            },
        ],
        "form_title": "Update Surge Pricing",
    }

    return render(
        request,
        "pricing/surge_form.html",
        context,
    )


@login_required
@permission_required("pricing.view_surgepricing", raise_exception=True)
def surge_detail(request, pk):
    surge = get_object_or_404(
        SurgePricing.objects.select_related(
            "city",
            "vehicle_type",
        ),
        pk=pk,
    )

    context = {
        "surge": surge,
        "page_title": "Surge Pricing Details",
        "breadcrumb_items": [
            {
                "title": "Surge Pricing Details",
                "url": "surge_detail",
            },
        ],
    }

    return render(
        request,
        "pricing/surge_detail.html",
        context,
    )


@login_required
@permission_required("pricing.change_surgepricing", raise_exception=True)
def surge_toggle(request, pk):
    if request.method != "POST":
        return redirect(
            "surge_detail",
            pk=pk,
        )

    surge = get_object_or_404(
        SurgePricing,
        pk=pk,
    )

    surge.is_active = not surge.is_active

    surge.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if surge.is_active:
        messages.success(
            request,
            "Surge pricing activated successfully.",
        )
    else:
        messages.success(
            request,
            "Surge pricing deactivated successfully.",
        )

    return redirect(
        "surge_detail",
        pk=surge.pk,
    )


@login_required
@permission_required("pricing.view_farebreakdown", raise_exception=True)
def fare_breakdown_list(request):
    fare_breakdowns = (
        FareBreakdown.objects.select_related(
            "ride",
        )
        .all()
        .order_by("-id")
    )

    context = {
        "fare_breakdowns": fare_breakdowns,
        "page_title": "Fare Breakdowns",
        "breadcrumb_items": [
            {
                "title": "Fare Breakdowns",
                "url": "fare_breakdown_list",
            },
        ],
        "total_breakdowns": fare_breakdowns.count(),
    }

    return render(
        request,
        "pricing/fare_breakdown_list.html",
        context,
    )


@login_required
@permission_required("pricing.view_farebreakdown", raise_exception=True)
def fare_breakdown_detail(request, pk):
    fare_breakdown = get_object_or_404(
        FareBreakdown.objects.select_related(
            "ride",
        ),
        pk=pk,
    )

    context = {
        "fare_breakdown": fare_breakdown,
        "page_title": "Fare Breakdown Details",
        "breadcrumb_items": [
            {
                "title": "Fare Breakdown Details",
                "url": "fare_breakdown_detail",
            },
        ],
    }

    return render(
        request,
        "pricing/fare_breakdown_detail.html",
        context,
    )