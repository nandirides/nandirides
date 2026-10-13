from django.contrib import admin

from .models import AppSetting


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "value",
        "data_type",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "data_type",
        "is_active",
    )

    search_fields = (
        "key",
        "value",
        "description",
    )

    ordering = (
        "-created_at",
    )
