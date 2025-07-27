from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminUser, IsAuthenticated
from users.serializers import (LoginSerializer, RegisterSerializer,
                               UserAdminSerializer, UserUpdateSerializer)

from .models import AuthToken

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Пользователь зарегистрирован"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response({
            "message": "Успешный вход",
            "user_id": data["user"].id,
            "token": data["token"]
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def delete(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Пользователь не аутентифицирован"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        deleted, _ = AuthToken.objects.filter(user=request.user).delete()
        return Response(
            {"message": "Вы вышли из системы"},
            status=status.HTTP_200_OK
        )


class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {'detail': 'Пользователь деактивирован'},
            status=status.HTTP_204_NO_CONTENT
        )
