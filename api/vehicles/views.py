from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from vehicles.models import VehicleType
from .serializers import VehicleTypeSerializer


class VehicleTypeListAPIView(generics.ListAPIView):
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VehicleType.objects.filter(
            is_active=True
        ).order_by("name")
