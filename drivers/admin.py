from django.contrib import admin

from .models import (
    Driver,
    DriverDocument,
    DriverBankAccount,
    DriverEarning,
    DriverPayout,
)


# ============================================================
# DRIVER
# ============================================================

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):

    list_display = (
        "driver_code",
        "user",
        "license_number",
        "status",
        "verification_status",
        "rating",
        "total_rides",
        "created_at",
    )

    list_filter = (
        "status",
        "verification_status",
        "created_at",
    )

    search_fields = (
        "driver_code",
        "license_number",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )

    autocomplete_fields = (
        "user",
    )

    readonly_fields = (
        "rating",
        "total_rides",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# DRIVER DOCUMENT
# ============================================================

@admin.register(DriverDocument)
class DriverDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "driver",
        "document_type",
        "document_number",
        "verification_status",
        "issue_date",
        "expiry_date",
        "verified_by",
        "verified_at",
    )

    list_filter = (
        "document_type",
        "verification_status",
        "issue_date",
        "expiry_date",
    )

    search_fields = (
        "driver__driver_code",
        "driver__user__username",
        "document_number",
    )

    autocomplete_fields = (
        "driver",
        "verified_by",
    )

    readonly_fields = (
        "verified_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# DRIVER BANK ACCOUNT
# ============================================================

@admin.register(DriverBankAccount)
class DriverBankAccountAdmin(admin.ModelAdmin):

    list_display = (
        "driver",
        "account_holder_name",
        "bank_name",
        "ifsc_code",
        "is_primary",
        "verification_status",
        "created_at",
    )

    list_filter = (
        "is_primary",
        "verification_status",
        "bank_name",
    )

    search_fields = (
        "driver__driver_code",
        "driver__user__username",
        "account_holder_name",
        "account_number",
        "ifsc_code",
        "bank_name",
        "upi_id",
    )

    autocomplete_fields = (
        "driver",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# DRIVER EARNING
# ============================================================

@admin.register(DriverEarning)
class DriverEarningAdmin(admin.ModelAdmin):

    list_display = (
        "driver",
        "ride",
        "gross_fare",
        "commission",
        "tax",
        "bonus",
        "penalty",
        "net_earning",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "driver__driver_code",
        "driver__user__username",
        "ride__ride_number",
    )

    autocomplete_fields = (
        "driver",
        "ride",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# DRIVER PAYOUT
# ============================================================

@admin.register(DriverPayout)
class DriverPayoutAdmin(admin.ModelAdmin):

    list_display = (
        "driver",
        "amount",
        "payment_method",
        "status",
        "payout_reference",
        "requested_at",
        "processed_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "requested_at",
        "processed_at",
    )

    search_fields = (
        "driver__driver_code",
        "driver__user__username",
        "payout_reference",
    )

    autocomplete_fields = (
        "driver",
    )

    readonly_fields = (
        "requested_at",
        "processed_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-requested_at",
    )