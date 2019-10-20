import jwt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from .models import User
from rate_your_movies.settings import SECRET_KEY


class JWTAuthentication(BaseAuthentication):
    model = None

    def _get_model(self):
        return User

    def authenticate(self, request):
        auth_token = get_authorization_header(request).split()
        if not auth_token or auth_token[0].decode("utf-8") != 'Bearer':
            return None
        if len(auth_token) == 1 or len(auth_token) > 2:
            raise AuthenticationFailed("Invalid token header provided.")

        return self.authenticate_credentials(auth_token[1])

    def authenticate_credentials(self, auth_token):
        self.model = self._get_model()
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
        except (jwt.exceptions.ExpiredSignature, jwt.exceptions.DecodeError,
                jwt.exceptions.InvalidTokenError, ValueError):
            raise AuthenticationFailed({"error": "Invalid token."})
        try:
            email = payload["email"]
            user = User().get_user_by_params(email=email, is_active=True)
        except ObjectDoesNotExist:
            raise AuthenticationFailed({"error": "User with such credentials does not exist."})
        user_token = user.token.encode()
        if not user_token:
            raise AuthenticationFailed({"error": "User is not logged in."})
        if user_token != auth_token:
            raise AuthenticationFailed({"error": "Authorization token has expired."})
        return user, auth_token

    def authenticate_header(self, request):
        return 'Bearer'
