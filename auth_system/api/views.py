from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import (AllowAny, IsAdminUser, IsAuthenticated)


MOCK_POSTS = [
    {"id": 1, "title": "Пост 1", "author": "user1@example.com"},
    {"id": 2, "title": "Пост 2", "author": "user2@example.com"},
]


class PublicMockView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'message': 'Публичный ресурс доступен всем'})


class UserMockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {'message': (
                f'Приватный ресурс для пользователя: {request.user.email}'
            )}
        )


class AdminMockView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({'message': 'Данные для админа'})
