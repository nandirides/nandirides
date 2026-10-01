from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import RideViewSet


router = DefaultRouter()

router.register(
    "",
    RideViewSet,
    basename="ride",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]