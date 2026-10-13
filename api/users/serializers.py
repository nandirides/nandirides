
from django.contrib.auth import get_user_model
from rest_framework import serializers

from dashboard.models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "username",
            "is_active",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # UserProfile se phone number read karein.
        try:
            data["phone"] = instance.profile.phone
        except UserProfile.DoesNotExist:
            data["phone"] = ""

        return data

    def update(self, instance, validated_data):
        # Phone ko User table ke bajaye UserProfile mein save karein.
        phone = validated_data.pop("phone", None)

        # Baaki fields, jaise name aur email, update karein.
        instance = super().update(instance, validated_data)

        # Phone bheja gaya ho tabhi usse update karein.
        if phone is not None:
            profile, created = UserProfile.objects.get_or_create(
                user=instance
            )
            profile.phone = phone
            profile.save(update_fields=["phone", "updated_at"])

        return instance
    
