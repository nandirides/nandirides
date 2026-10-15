
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import tracking_api
from .driver_views import (
    DriverRideRequestsAPIView,
    DriverAcceptRideAPIView,
    DriverRideDetailsAPIView,
)

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
        "fare/estimate/",
        FareEstimationAPIView.as_view(),
        name="fare-estimate",
    ),

    path(
        "driver/requests/",
        DriverRideRequestsAPIView.as_view(),
        name="driver-ride-requests",
    ),

    path(
        "driver/requests/<int:request_id>/accept/",
        DriverAcceptRideAPIView.as_view(),
        name="driver-accept-ride",
    ),

    path(
        "requests/<int:request_id>/tracking/",
        tracking_api.ride_request_tracking,
        name="ride-request-tracking",
    ),
    path(
        "<int:ride_id>/tracking/update/",
        tracking_api.driver_update_ride_location,
        name="driver-update-ride-location",
    ),
    path(
        "<int:ride_id>/status/",
        tracking_api.driver_update_ride_status,
        name="driver-update-ride-status",
    ),
    path(
    "driver/rides/<int:ride_id>/",
    DriverRideDetailsAPIView.as_view(),
    name="driver-ride-details",
),

    path("", include(router.urls)),
]