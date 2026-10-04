from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from rides.models import Ride, RideRequest
from locations.models import Location
from vehicles.models import VehicleType
from promotions.models import Coupon
from .services import calculate_fare

class FareEstimationSerializer(serializers.Serializer):
    pickup_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    drop_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    vehicle_type = serializers.PrimaryKeyRelatedField(
        queryset=VehicleType.objects.filter(is_active=True)
    )
    distance_km = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    duration_minutes = serializers.IntegerField(
        read_only=True
    )
    base_fare = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    distance_fare = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    time_fare = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    discount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    final_fare = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )
    coupon_message = serializers.CharField(
        read_only=True
    )

    def validate(self, attrs):
        if attrs["pickup_location"].id == attrs["drop_location"].id:
            raise serializers.ValidationError({
                "drop_location": "Pickup and drop location cannot be the same."
            })
        return attrs

class RideRequestSerializer(serializers.ModelSerializer):
    pickup_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    drop_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    vehicle_type = serializers.PrimaryKeyRelatedField(
        queryset=VehicleType.objects.filter(is_active=True)
    )
    passenger = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    request_number = serializers.CharField(
        read_only=True
    )
    estimated_distance = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    estimated_duration = serializers.IntegerField(
        read_only=True
    )
    estimated_fare = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    coupon = serializers.PrimaryKeyRelatedField(
        queryset=Coupon.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )
    discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    final_fare = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    status = serializers.CharField(
        read_only=True
    )
    requested_at = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        model = RideRequest
        fields = [
            "id",
            "request_number",
            "passenger",
            "pickup_location",
            "drop_location",
            "vehicle_type",
            "requested_at",
            "scheduled_at",
            "estimated_distance",
            "estimated_duration",
            "estimated_fare",
            "coupon",
            "discount_amount",
            "final_fare",
            "status",
        ]
        read_only_fields = [
            "id",
            "request_number",
            "passenger",
            "requested_at",
            "estimated_distance",
            "estimated_duration",
            "estimated_fare",
            "discount_amount",
            "final_fare",
            "status",
        ]

    def validate(self, attrs):
        if attrs["pickup_location"].id == attrs["drop_location"].id:
            raise serializers.ValidationError({
                "drop_location": "Pickup and drop location cannot be the same."
            })
        scheduled_at = attrs.get("scheduled_at")
        if scheduled_at and scheduled_at <= timezone.now():
            raise serializers.ValidationError({
                "scheduled_at": "Scheduled time must be in the future."
            })
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        pickup = validated_data["pickup_location"]
        drop = validated_data["drop_location"]
        vehicle_type = validated_data["vehicle_type"]
        coupon = validated_data.pop("coupon", None)
        coupon_code = coupon.code if coupon else ""
        fare = calculate_fare(
            pickup=pickup,
            drop=drop,
            vehicle_type=vehicle_type,
            user=user,
            coupon_code=coupon_code
        )
        request_number = self.generate_request_number()
        ride_request = RideRequest.objects.create(
            request_number=request_number,
            passenger=user,
            estimated_distance=fare["distance_km"],
            estimated_duration=fare["duration_minutes"],
            estimated_fare=fare["subtotal"],
            coupon=coupon if fare["discount"] > 0 else None,
            discount_amount=fare["discount"],
            final_fare=fare["final_fare"],
            **validated_data
        )
        return ride_request

    def generate_request_number(self):
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        return f"RR{timestamp}"
    
class RideSerializer(serializers.ModelSerializer):
    passenger_name = serializers.CharField(
        source="passenger.username",
        read_only=True
    )
    driver_name = serializers.SerializerMethodField()
    vehicle_number = serializers.CharField(
        source="vehicle.vehicle_number",
        read_only=True
    )
    vehicle_type = serializers.CharField(
        source="vehicle.vehicle_type.name",
        read_only=True
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

    def get_driver_name(self, obj):
        if not obj.driver:
            return None
        if not obj.driver.user:
            return obj.driver.driver_code
        return (
            obj.driver.user.get_full_name()
            or obj.driver.user.username
        )