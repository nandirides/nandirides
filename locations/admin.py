from django.contrib import admin

from .models import (
    Country,
    State,
    City,
    Location,
)


# ============================================================
# COUNTRY
# ============================================================

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "code",
    )

    ordering = (
        "name",
    )


# ============================================================
# STATE
# ============================================================

@admin.register(State)
class StateAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "country",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "country",
    )

    search_fields = (
        "name",
        "country__name",
    )

    autocomplete_fields = (
        "country",
    )

    ordering = (
        "country",
        "name",
    )


# ============================================================
# CITY
# ============================================================

@admin.register(City)
class CityAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "state",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "state",
        "state__country",
    )

    search_fields = (
        "name",
        "state__name",
        "state__country__name",
    )

    autocomplete_fields = (
        "state",
    )

    ordering = (
        "state",
        "name",
    )


# ============================================================
# LOCATION
# ============================================================

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    list_display = (
        "address",
        "city",
        "latitude",
        "longitude",
        "created_at",
    )

    list_filter = (
        "city",
        "city__state",
        "city__state__country",
    )

    search_fields = (
        "address",
        "city__name",
        "city__state__name",
    )

    autocomplete_fields = (
        "city",
    )

    ordering = (
        "-created_at",
    )