from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import FareEstimationAPIView, RideRequestViewSet, RideViewSet

router = DefaultRouter()

router.register(
    "requests",
    RideRequestViewSet,
    basename="ride-request"
)

router.register(
    "",
    RideViewSet,
    basename="ride"
)

urlpatterns = [
    path(
        "fare-estimate/",
        FareEstimationAPIView.as_view(),
        name="fare-estimate"
    ),
    path(
        "",
        include(router.urls)
    ),
]