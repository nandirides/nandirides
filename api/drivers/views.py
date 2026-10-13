
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from drivers.models import Driver, DriverDocument, DriverBankAccount
from .serializers import (
    DriverRegistrationSerializer,
    DriverProfileSerializer,
    DriverDocumentSerializer,
    DriverBankAccountSerializer,
)


class DriverRegistrationAPIView(generics.CreateAPIView):
    serializer_class = DriverRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if Driver.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Driver profile already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()

        return Response(
            {
                "message": "Driver registration submitted successfully.",
                "driver": DriverProfileSerializer(driver).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DriverMyProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = DriverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return generics.get_object_or_404(
            Driver,
            user=self.request.user,
        )


class DriverOnlineStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return Response(
                {"detail": "Driver profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if driver.status != Driver.Status.ACTIVE:
            return Response(
                {"detail": "Your driver account is not active yet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_online = request.data.get("is_online")

        if not isinstance(is_online, bool):
            return Response(
                {"is_online": "Send true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        driver.is_online = is_online
        driver.save(update_fields=["is_online", "updated_at"])

        return Response({
            "message": "Driver availability updated.",
            "is_online": driver.is_online,
        })


class DriverDocumentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DriverDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DriverDocument.objects.filter(
            driver__user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        driver = Driver.objects.get(user=self.request.user)
        serializer.save(driver=driver)


class DriverBankAccountListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DriverBankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DriverBankAccount.objects.filter(
            driver__user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        driver = Driver.objects.get(user=self.request.user)
        serializer.save(driver=driver)