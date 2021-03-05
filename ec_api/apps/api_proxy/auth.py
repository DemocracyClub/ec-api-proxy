from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission

from users.models import APIKey


class TokenWithGetParamAuthentication(TokenAuthentication):
    model = APIKey
    keyword = "Token"

    def authenticate(self, request):
        """
        If token param is in the request GET set that as the HTTP_AUTHORIZATION header
        """
        token = request.GET.get(self.keyword.lower())
        if token:
            request.META["HTTP_AUTHORIZATION"] = f"{self.keyword} {token}"

        return super().authenticate(request)

    def authenticate_credentials(self, key):
        """
        Attempt to authenticate the api key. On success returns the user and
        API key object to be added to the request.
        """
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")
        return (token.user, token)


class IsValidAPIUser(BasePermission):
    """
    Allows access only to users that have a API key
    """

    def has_permission(self, request, view):
        try:
            return request.user.api_keys.exists()
        except AttributeError:
            return False
