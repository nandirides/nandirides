from django.urls import path
from dashboard import views


# app_name = "admindashboard"

urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
        "account/profile/",
        views.admin_profile,
        name="admin_profile",
    ),
    path(
        "account/editprofile/",
        views.edit_admin_profile,
        name="edit_admin_profile",
    ),
    path(
        "account/setting/",
        views.user_setting,
        name="user_setting",
    ),
    path(
        "users/<int:user_id>/profile/",
        views.user_profile,
        name="user_profile",
    ),
    path(
        "users/ridestatus/",
        views.user_ridestatus,
        name="user_ridestatus",
    ),
    path(
        "gallery/",
        views.ride_gallery,
        name="ride_gallery",
    ),
    path(
        "gallery/<int:pk>/delete/",
        views.gallery_delete,
        name="gallery_delete",
    ),
    path(
        "users/",
        views.user_list,
        name="user_list",
    ),
    path(
        "users/add/",
        views.user_create,
        name="user_create",
    ),
    path(
        "users/<int:pk>/delete/",
        views.user_delete,
        name="user_delete",
    ),
    # Update
    path(
        "<int:pk>/edit/",
        views.user_create,
        name="user_update",
    ),
    # User List Status Toggle
    path(
        "users/<int:pk>/status-toggle/",
        views.user_status_toggle,
        name="user_status_toggle",
    ),

    path(
    "users/rides/",
    views.ride_details,
    name="ride_details",
),
]