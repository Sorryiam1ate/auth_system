from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """Дополнительный пермишн"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Вы не вошли в систему")
        return True

    def has_object_permission(self, request, view, obj):
        print("🔍 has_object_permission called")
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Вы не вошли в систему")
        if request.user.role == 'admin':
            return True
        if obj.author == request.user:
            return True
        raise PermissionDenied("У вас нет прав для изменения этого объекта")


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )
