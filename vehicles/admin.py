from django.contrib import admin

from .models import (
    Vehicle,
    VehicleType,
)


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )

    search_fields = (
        "__str__",
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )

    search_fields = (
        "__str__",
    )
