from rest_framework import serializers

from vehicles.models import VehicleType


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = [
            "id",
            "name",
            "code",
            "description",
            "capacity",
            "base_fare",
            "per_km_rate",
            "per_minute_rate",
            "is_active",
        ]
        read_only_fields = fields