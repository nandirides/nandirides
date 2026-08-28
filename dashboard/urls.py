from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
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