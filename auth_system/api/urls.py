from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import (LoginView, LogoutView, RegisterView,
                         UserAdminViewSet, UserProfileView)

from api.views import (AdminMockView, PublicMockView,
                       UserMockView)

router = DefaultRouter()
router.register(r'admin/users', UserAdminViewSet, basename='user-admin')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile-update'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='login'),
    path('', include(router.urls)),

    path('public/', PublicMockView.as_view(), name='public-mock'),
    path('user/', UserMockView.as_view(), name='user-mock'),
    path('admin/', AdminMockView.as_view(), name='admin-mock'),
]
