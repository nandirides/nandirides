
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from locations.models import Country, State, City, Location
from .serializers import (
    CountrySerializer,
    StateSerializer,
    CitySerializer,
    LocationSerializer,
    MapLocationCreateSerializer,
)

class CountryListAPIView(generics.ListAPIView):
    queryset = Country.objects.all().order_by("name")
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]

class StateListAPIView(generics.ListAPIView):
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = State.objects.select_related("country").order_by("name")
        country_id = self.request.query_params.get("country")
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset

class CityListAPIView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = City.objects.select_related("state", "state__country").order_by("name")
        state_id = self.request.query_params.get("state")
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        return queryset

class LocationListAPIView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Location.objects.select_related("city", "city__state").order_by("address")
        city_id = self.request.query_params.get("city")
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset

class MapLocationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = MapLocationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Map location saved successfully.",
                "data": LocationSerializer(location).data,
            },
            status=status.HTTP_201_CREATED,
        )
