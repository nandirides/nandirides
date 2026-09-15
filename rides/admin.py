from django.contrib import admin

from .models import (
    RideRequest,
    Ride,
    RideStop,
    RideDriverAssignment,
    RideTracking,
    CancellationReason,
    RideCancellation,
    RideRating,
)


# ============================================================
# RIDE REQUEST
# ============================================================

@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):

    list_display = (
        "request_number",
        "passenger",
        "pickup_location",
        "drop_location",
        "vehicle_type",
        "scheduled_at",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "vehicle_type",
        "scheduled_at",
        "created_at",
    )

    search_fields = (
        "request_number",
        "passenger__username",
        "passenger__first_name",
        "passenger__last_name",
    )

    autocomplete_fields = (
        "passenger",
        "pickup_location",
        "drop_location",
        "vehicle_type",
    )

    readonly_fields = (
        "requested_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# RIDE
# ============================================================

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):

    list_display = (
        "ride_number",
        "ride_request",
        "passenger",
        "driver",
        "vehicle",
        "distance_km",
        "duration_minutes",
        "status",
        "scheduled_at",
        "started_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "scheduled_at",
        "started_at",
        "completed_at",
        "created_at",
    )

    search_fields = (
        "ride_number",
        "passenger__username",
        "passenger__first_name",
        "passenger__last_name",
        "driver__driver_code",
    )

    autocomplete_fields = (
        "ride_request",
        "passenger",
        "driver",
        "vehicle",
        "pickup_location",
        "drop_location",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# RIDE STOP
# ============================================================

@admin.register(RideStop)
class RideStopAdmin(admin.ModelAdmin):

    list_display = (
        "ride",
        "stop_order",
        "location",
        "arrival_time",
        "departure_time",
        "status",
    )

    list_filter = (
        "status",
        "arrival_time",
        "departure_time",
    )

    search_fields = (
        "ride__ride_number",
        "location__address",
    )

    autocomplete_fields = (
        "ride",
        "location",
    )

    ordering = (
        "ride",
        "stop_order",
    )


# ============================================================
# RIDE DRIVER ASSIGNMENT
# ============================================================

@admin.register(RideDriverAssignment)
class RideDriverAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "ride",
        "driver",
        "status",
        "assigned_at",
        "accepted_at",
        "rejected_at",
    )

    list_filter = (
        "status",
        "assigned_at",
        "accepted_at",
        "rejected_at",
    )

    search_fields = (
        "ride__ride_number",
        "driver__driver_code",
        "driver__user__username",
    )

    autocomplete_fields = (
        "ride",
        "driver",
    )

    readonly_fields = (
        "assigned_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-assigned_at",
    )


# ============================================================
# RIDE TRACKING
# ============================================================

@admin.register(RideTracking)
class RideTrackingAdmin(admin.ModelAdmin):

    list_display = (
        "ride",
        "driver",
        "latitude",
        "longitude",
        "speed",
        "heading",
        "accuracy",
        "recorded_at",
    )

    list_filter = (
        "recorded_at",
    )

    search_fields = (
        "ride__ride_number",
        "driver__driver_code",
    )

    autocomplete_fields = (
        "ride",
        "driver",
    )

    readonly_fields = (
        "recorded_at",
    )

    ordering = (
        "-recorded_at",
    )


# ============================================================
# CANCELLATION REASON
# ============================================================

@admin.register(CancellationReason)
class CancellationReasonAdmin(admin.ModelAdmin):

    list_display = (
        "reason",
        "type",
        "charge_applicable",
        "charge_amount",
        "is_active",
        "created_at",
    )

    list_filter = (
        "type",
        "charge_applicable",
        "is_active",
    )

    search_fields = (
        "reason",
    )

    ordering = (
        "type",
        "reason",
    )


# ============================================================
# RIDE CANCELLATION
# ============================================================

@admin.register(RideCancellation)
class RideCancellationAdmin(admin.ModelAdmin):

    list_display = (
        "ride",
        "cancelled_by",
        "reason",
        "cancellation_charge",
        "cancelled_at",
    )

    list_filter = (
        "reason__type",
        "cancelled_at",
    )

    search_fields = (
        "ride__ride_number",
        "cancelled_by__username",
        "reason__reason",
    )

    autocomplete_fields = (
        "ride",
        "cancelled_by",
        "reason",
    )

    readonly_fields = (
        "cancelled_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-cancelled_at",
    )


# ============================================================
# RIDE RATING
# ============================================================

@admin.register(RideRating)
class RideRatingAdmin(admin.ModelAdmin):

    list_display = (
        "ride",
        "from_user",
        "to_user",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "ride__ride_number",
        "from_user__username",
        "to_user__username",
        "review",
    )

    autocomplete_fields = (
        "ride",
        "from_user",
        "to_user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )
