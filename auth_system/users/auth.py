from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from users.models import AuthToken

TOKEN_PREFIX = "Token "


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith(TOKEN_PREFIX):
            return None

        token_key = auth_header[len(TOKEN_PREFIX):]
        try:
            token = AuthToken.objects.select_related('user').get(key=token_key)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token.")
        if not token.user.is_active:
            raise AuthenticationFailed("User is deactivated.")
        return (token.user, None)
