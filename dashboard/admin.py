from django.contrib import admin

from .models import Gallery

@admin.register(Gallery)
class ProfileImage(admin.ModelAdmin):
    list_display = ['id','profile_image','date']
