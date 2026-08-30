from django.urls import path
from . import views

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
        "users/",
        views.user_list,
        name="user_list",
    ),

    path(
        "users/add/",
        views.user_create,
        name="user_create",
    ),
]