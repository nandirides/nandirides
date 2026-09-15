from django.contrib import admin

from .models import (
    Coupon,
    CouponUsage,
)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )

    search_fields = (
        "__str__",
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )

    search_fields = (
        "__str__",
    )
