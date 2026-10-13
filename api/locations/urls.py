
from django.urls import path
from .views import (
    CountryListAPIView,
    StateListAPIView,
    CityListAPIView,
    LocationListAPIView,
    MapLocationCreateAPIView,
)

urlpatterns = [
    path("countries/", CountryListAPIView.as_view(), name="country-list"),
    path("states/", StateListAPIView.as_view(), name="state-list"),
    path("cities/", CityListAPIView.as_view(), name="city-list"),
    path("locations/map-select/", MapLocationCreateAPIView.as_view(), name="map-location-create"),
    path("locations/", LocationListAPIView.as_view(), name="location-list"),
]
