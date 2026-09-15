from django.contrib import admin

from .models import Gallery

from .models import (
    UserProfile,
    UserAddress,
)


@admin.register(Gallery)
class ProfileImage(admin.ModelAdmin):
    list_display = ['id','profile_image','date']



# ============================================================
# USER PROFILE
# ============================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "phone",
        "gender",
        "date_of_birth",
        "city",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "gender",
        "city",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
    )

    autocomplete_fields = (
        "user",
        "city",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# USER ADDRESS
# ============================================================

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "address_type",
        "city",
        "postal_code",
        "is_default",
        "created_at",
    )

    list_filter = (
        "address_type",
        "is_default",
        "city",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "address_line1",
        "address_line2",
        "postal_code",
    )

    autocomplete_fields = (
        "user",
        "city",
    )

    ordering = (
        "-created_at",
    )
