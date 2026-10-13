
from django.urls import path

from .views import (
    DriverRegistrationAPIView,
    DriverMyProfileAPIView,
    DriverOnlineStatusAPIView,
    DriverDocumentListCreateAPIView,
    DriverBankAccountListCreateAPIView,
)

app_name = "driver_api"

urlpatterns = [
    path("register/", DriverRegistrationAPIView.as_view(), name="register"),
    path("me/", DriverMyProfileAPIView.as_view(), name="my-profile"),
    path(
        "online-status/",
        DriverOnlineStatusAPIView.as_view(),
        name="online-status",
    ),
    path(
        "documents/",
        DriverDocumentListCreateAPIView.as_view(),
        name="documents",
    ),
    path(
        "bank-accounts/",
        DriverBankAccountListCreateAPIView.as_view(),
        name="bank-accounts",
    ),
]