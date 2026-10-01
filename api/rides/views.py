from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from rides.models import Ride

from .serializers import RideSerializer


class RideViewSet(
    viewsets.ModelViewSet
):

    serializer_class = RideSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return (
            Ride.objects
            .select_related(
                "passenger",
                "driver",
                "driver__user",
                "vehicle",
                "vehicle__vehicle_type",
                "ride_request",
                "pickup_location",
                "drop_location",
            )
            .filter(
                passenger=self.request.user,
            )
            .order_by(
                "-created_at",
            )
        )