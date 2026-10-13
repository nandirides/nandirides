
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FareEstimationAPIView,
    RideRequestViewSet,
    RideViewSet,
)
from .driver_views import (
    DriverRideRequestsAPIView,
    DriverAcceptRideAPIView,
)

router = DefaultRouter()
router.register("requests", RideRequestViewSet, basename="ride-request")
router.register("", RideViewSet, basename="ride")

urlpatterns = [
    path(
        "fare-estimate/",
        FareEstimationAPIView.as_view(),
        name="fare-estimate",
    ),

    path(
        "driver-requests/",
        DriverRideRequestsAPIView.as_view(),
        name="driver-ride-requests",
    ),

    path(
        "driver-requests/<int:request_id>/accept/",
        DriverAcceptRideAPIView.as_view(),
        name="driver-accept-ride",
    ),

    path("", include(router.urls)),
]