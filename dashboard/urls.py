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
        views.user_profile,
        name="user_profile",
    ),

    path(
        "account/setting/",
        views.user_setting,
        name="user_setting",
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
] 