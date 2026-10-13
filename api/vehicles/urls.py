from django.urls import path

from .views import VehicleTypeListAPIView

urlpatterns = [
    path(
        "types/",
        VehicleTypeListAPIView.as_view(),
        name="vehicle-type-list",
    ),
]
