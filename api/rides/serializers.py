from rest_framework import serializers

from rides.models import Ride


class RideSerializer(
    serializers.ModelSerializer
):

    passenger_name = serializers.CharField(
        source="passenger.username",
        read_only=True,
    )

    driver_name = serializers.SerializerMethodField()

    vehicle_number = serializers.CharField(
        source="vehicle.vehicle_number",
        read_only=True,
    )

    vehicle_type = serializers.CharField(
        source="vehicle.vehicle_type.name",
        read_only=True,
    )

    class Meta:

        model = Ride

        fields = [
            "id",
            "ride_number",
            "ride_request",

            "passenger",
            "passenger_name",

            "driver",
            "driver_name",

            "vehicle",
            "vehicle_number",
            "vehicle_type",

            "pickup_location",
            "drop_location",

            "scheduled_at",

            "distance_km",
            "duration_minutes",

            "status",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "ride_number",
            "passenger_name",
            "driver_name",
            "vehicle_number",
            "vehicle_type",
            "created_at",
            "updated_at",
        ]

    def get_driver_name(
        self,
        obj,
    ):

        if not obj.driver:
            return None

        if not obj.driver.user:
            return obj.driver.driver_code

        return (
            obj.driver.user.get_full_name()
            or obj.driver.user.username
        )