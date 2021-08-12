from django.core.cache import cache

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission

from users.models import APIKey, CustomUser


class TokenWithGetParamAuthentication(TokenAuthentication):
    model = APIKey
    keyword = "Token"
    invalid_string = "invalid"

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

        # First try to get the key from the cache
        cached_user = cache.get(key)
        if cached_user is None:
            # We've not cached this key before. We need to see if it's valid
            model = self.get_model()
            try:
                token = model.objects.get(key=key)
                # The User is valid, so set the cache with the value being a
                # dict with the User PK
                cached_user = {"pk": token.user.pk}
                cache.set(key, cached_user, 60 * 5)
            except model.DoesNotExist:
                # This isn't a valid key. To prevent this being a way to bruit
                # force the database, we'll cache the key with a string that
                # tells us it's invalid

                # Cache invalid keys for 30 minutes
                cache.set(key, self.invalid_string, 60 * 30)
                cached_user = self.invalid_string

        if cached_user == self.invalid_string:
            # If we've seen an invalid key, fail authrntication
            raise exceptions.AuthenticationFailed("Invalid token.")

        # Construct a CustomUser object to return. This isn't a saved object
        # but if the actual object is needed downstream we can either call
        # `refresh_from_db()` on it, or add more attributes to the cached dict
        # above
        user_obj = CustomUser(**cached_user)
        user_obj.auth_check_keys = False

        # return the user object, and the API key
        return user_obj, key


class IsValidAPIUser(BasePermission):
    """
    Allows access only to users that have a API key
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # If we're authenticated, we always have permission
            return True
        return False
