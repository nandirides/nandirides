from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer


class LoginAPIView(APIView):

    authentication_classes = []

    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data["user"]

        token, created = (
            Token.objects.get_or_create(
                user=user
            )
        )

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):

    authentication_classes = [
        TokenAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):

        token = request.auth

        if token:
            token.delete()

        return Response(
            {
                "success": True,
                "message": "Logout successful.",
            },
            status=status.HTTP_200_OK,
        )