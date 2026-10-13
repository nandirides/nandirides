
from rest_framework import serializers
from locations.models import Country, State, City, Location

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code"]

class StateSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)
    class Meta:
        model = State
        fields = ["id", "name", "country", "country_name"]

class CitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    country_name = serializers.CharField(source="state.country.name", read_only=True)
    class Meta:
        model = City
        fields = ["id", "name", "state", "state_name", "country_name"]

class LocationSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True, allow_null=True)
    state_name = serializers.CharField(source="city.state.name", read_only=True, allow_null=True)
    class Meta:
        model = Location
        fields = ["id", "address", "city", "city_name", "state_name", "latitude", "longitude"]

class MapLocationCreateSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=500)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate_address(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Address cannot be empty.")
        return value

    def create(self, validated_data):
        city = validated_data.get("city")
        location = Location.objects.filter(
            latitude=validated_data["latitude"],
            longitude=validated_data["longitude"],
            address=validated_data["address"],
            city=city,
        ).first()
        if location:
            return location
        return Location.objects.create(**validated_data)
