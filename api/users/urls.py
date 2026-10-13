from django.urls import path

from .views import UserDetailAPIView


urlpatterns = [

    path(
        "",
        UserDetailAPIView.as_view(),
        name="user-me",
    ),
]