
from django.contrib import admin

from .models import Coupon, CouponUsage


# ============================================================
# COUPON
# ============================================================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "discount_type",
        "discount_value",
        "maximum_discount",
        "minimum_fare",
        "usage_limit",
        "per_user_limit",
        "valid_from",
        "valid_to",
        "is_active",
        "created_at",
    )

    list_filter = (
        "discount_type",
        "is_active",
        "valid_from",
        "valid_to",
        "created_at",
    )

    search_fields = (
        "code",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    fieldsets = (
        (
            "Coupon Information",
            {
                "fields": (
                    "code",
                    "name",
                    "is_active",
                )
            },
        ),
        (
            "Discount",
            {
                "fields": (
                    "discount_type",
                    "discount_value",
                    "maximum_discount",
                    "minimum_fare",
                )
            },
        ),
        (
            "Usage Limits",
            {
                "fields": (
                    "usage_limit",
                    "per_user_limit",
                )
            },
        ),
        (
            "Validity",
            {
                "fields": (
                    "valid_from",
                    "valid_to",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


# ============================================================
# COUPON USAGE
# ============================================================

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):

    list_display = (
        "coupon",
        "user",
        "ride",
        "discount_amount",
        "used_at",
        "created_at",
    )

    list_filter = (
        "coupon",
        "used_at",
        "created_at",
    )

    search_fields = (
        "coupon__code",
        "coupon__name",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "ride__ride_number",
    )

    autocomplete_fields = (
        "coupon",
        "user",
        "ride",
    )

    readonly_fields = (
        "used_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-used_at",
    )

    list_per_page = 25
