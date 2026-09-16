from django.contrib import admin
from .models import VehicleType, Vehicle, DriverVehicle, VehicleDocument
@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "capacity",
        "base_fare",
        "per_km_rate",
        "per_minute_rate",
        "is_active",
        "created_at",
    )
    list_display_links = (
        "name",
        "code",
    )
    list_filter = (
        "is_active",
        "capacity",
    )
    search_fields = (
        "name",
        "code",
        "description",
    )
    ordering = (
        "name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Vehicle Type Information",
            {
                "fields": (
                    "name",
                    "code",
                    "description",
                    "capacity",
                )
            },
        ),
        (
            "Fare Configuration",
            {
                "fields": (
                    "base_fare",
                    "per_km_rate",
                    "per_minute_rate",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
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
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle_number",
        "vehicle_type",
        "brand",
        "model",
        "fuel_type",
        "seating_capacity",
        "registration_expiry",
        "status",
        "created_at",
    )
    list_display_links = (
        "vehicle_number",
    )
    list_filter = (
        "status",
        "fuel_type",
        "vehicle_type",
        "registration_date",
        "registration_expiry",
    )
    search_fields = (
        "vehicle_number",
        "brand",
        "model",
        "variant",
        "color",
    )
    ordering = (
        "-created_at",
    )
    date_hierarchy = "created_at"
    list_per_page = 25
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    autocomplete_fields = (
        "vehicle_type",
    )
    fieldsets = (
        (
            "Vehicle Information",
            {
                "fields": (
                    "vehicle_number",
                    "vehicle_type",
                    "brand",
                    "model",
                    "variant",
                    "color",
                )
            },
        ),
        (
            "Vehicle Specifications",
            {
                "fields": (
                    "manufacturing_year",
                    "fuel_type",
                    "seating_capacity",
                )
            },
        ),
        (
            "Registration Details",
            {
                "fields": (
                    "registration_date",
                    "registration_expiry",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
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
@admin.register(DriverVehicle)
class DriverVehicleAdmin(admin.ModelAdmin):
    list_display = (
        "driver",
        "vehicle",
        "assigned_from",
        "assigned_to",
        "is_current",
        "created_at",
    )
    list_display_links = (
        "driver",
        "vehicle",
    )
    list_filter = (
        "is_current",
        "assigned_from",
        "assigned_to",
        "vehicle__vehicle_type",
    )
    search_fields = (
        "driver__first_name",
        "driver__last_name",
        "vehicle__vehicle_number",
        "vehicle__brand",
        "vehicle__model",
    )
    ordering = (
        "-assigned_from",
    )
    date_hierarchy = "assigned_from"
    list_per_page = 25
    autocomplete_fields = (
        "driver",
        "vehicle",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Assignment",
            {
                "fields": (
                    "driver",
                    "vehicle",
                    "assigned_from",
                    "assigned_to",
                    "is_current",
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
@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "document_type",
        "document_number",
        "issue_date",
        "expiry_date",
        "verification_status",
        "created_at",
    )
    list_display_links = (
        "vehicle",
        "document_type",
    )
    list_filter = (
        "document_type",
        "verification_status",
        "issue_date",
        "expiry_date",
    )
    search_fields = (
        "vehicle__vehicle_number",
        "document_number",
    )
    ordering = (
        "expiry_date",
        "-created_at",
    )
    date_hierarchy = "expiry_date"
    list_per_page = 25
    autocomplete_fields = (
        "vehicle",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Document Information",
            {
                "fields": (
                    "vehicle",
                    "document_type",
                    "document_number",
                    "document_file",
                )
            },
        ),
        (
            "Validity",
            {
                "fields": (
                    "issue_date",
                    "expiry_date",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    "verification_status",
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
