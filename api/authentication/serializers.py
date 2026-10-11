from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.apps import apps
from django.db import transaction

User = get_user_model()

class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False
    )
    password2 = serializers.CharField(
        write_only=True,
        trim_whitespace=False
    )

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already registered."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({
                "password2": "Passwords do not match."
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password2")
        phone = validated_data.pop("phone")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
            password=password,
        )

        # UserProfile model ka app label "users" hona chahiye.
        Profile = apps.get_model("dashboard", "UserProfile")
        Profile.objects.get_or_create(
            user=user,
            defaults={"phone": phone},
        )

        return user
    
class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        style={
            "input_type": "password",
        },
    )

    def validate(self, attrs):

        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:

            raise serializers.ValidationError(
                "Username and password are required."
            )

        user = authenticate(
            username=username,
            password=password,
        )

        if not user:

            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:

            raise serializers.ValidationError(
                "User account is inactive."
            )

        attrs["user"] = user

        return attrs