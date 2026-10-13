
from django.contrib.auth import get_user_model
from rest_framework import serializers

from drivers.models import (
    Driver,
    DriverDocument,
    DriverBankAccount,
    DriverEarning,
    DriverPayout,
)

User = get_user_model()


class DriverRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="user.first_name", required=True
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True
    )
    email = serializers.EmailField(
        source="user.email", required=False, allow_blank=True
    )

    class Meta:
        model = Driver
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "license_number",
            "license_expiry",
            "experience_years",
        ]
        read_only_fields = ["id"]

    def validate_phone(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Mobile number is required."
            )
        if Driver.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "This mobile number is already registered."
            )
        return value

    def validate_license_number(self, value):
        value = value.strip().upper()
        if Driver.objects.filter(license_number=value).exists():
            raise serializers.ValidationError(
                "This license number is already registered."
            )
        return value

    def create(self, validated_data):
        user_data = validated_data.pop("user", {})
        request = self.context["request"]

        user = request.user
        user.first_name = user_data.get("first_name", "")
        user.last_name = user_data.get("last_name", "")
        user.email = user_data.get("email", "")
        user.save()

        validated_data["user"] = user
        validated_data["driver_code"] = (
            f"DRV-{user.pk}"
        )

        return Driver.objects.create(**validated_data)


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "id",
            "phone",
            "driver_code",
            "license_number",
            "license_expiry",
            "experience_years",
            "status",
            "verification_status",
            "is_online",
            "rating",
            "total_rides",
        ]
        read_only_fields = [
            "id",
            "driver_code",
            "status",
            "verification_status",
            "rating",
            "total_rides",
        ]


class DriverDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDocument
        fields = [
            "id",
            "document_type",
            "document_number",
            "document_file",
            "issue_date",
            "expiry_date",
            "verification_status",
        ]
        read_only_fields = ["id", "verification_status"]


class DriverBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverBankAccount
        fields = [
            "id",
            "account_holder_name",
            "account_number",
            "ifsc_code",
            "bank_name",
            "upi_id",
            "is_primary",
            "verification_status",
        ]
        read_only_fields = ["id", "verification_status"]


class DriverEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverEarning
        fields = "__all__"
        read_only_fields = ["id"]


class DriverPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverPayout
        fields = "__all__"
        read_only_fields = ["id", "status", "requested_at", "processed_at"]