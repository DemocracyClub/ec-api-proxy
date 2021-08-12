from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
import pytest

from api_proxy.auth import IsValidAPIUser, TokenWithGetParamAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import CustomUser

from users.tests.factories import APIKey

User = get_user_model()


class TestTokenWithGetParamAuthentication:
    @pytest.fixture
    def api_key(self):
        """
        Returns a generated API key string
        """
        return APIKey()._generate_key()

    def test_authenticate_with_header(self, api_key, rf, mocker):
        """
        Test that when token passed in the header it is used to
        authenticate credentials
        """
        auth_obj = TokenWithGetParamAuthentication()
        request = rf.get("/api/v1/postcode/TE11ST")
        token = f"{auth_obj.keyword} {api_key}"
        request.META["HTTP_AUTHORIZATION"] = token

        mocker.patch.object(auth_obj, "authenticate_credentials")

        auth_obj.authenticate(request=request)

        # check the header has been unchanged
        assert request.META["HTTP_AUTHORIZATION"] == token
        auth_obj.authenticate_credentials.assert_called_once_with(api_key)

    def test_authenticate_with_token_param(self, rf, api_key, mocker):
        """
        Test that when token is passed in the querystring it is used to
        authenticate credentials
        """
        auth_obj = TokenWithGetParamAuthentication()
        request = rf.get(
            f"/api/v1/postcode/TE11ST?{auth_obj.keyword.lower()}={api_key}"
        )
        request.META["HTTP_AUTHORIZATION"] = None
        mocker.patch.object(auth_obj, "authenticate_credentials")
        auth_obj.authenticate(request=request)

        # check the header has been set
        expected = f"{auth_obj.keyword} {api_key}"
        assert request.META["HTTP_AUTHORIZATION"] == expected
        auth_obj.authenticate_credentials.assert_called_once_with(api_key)

    def test_authenticate_credentials_without_key(self, mocker):
        """
        Test auth exception is raised when key is not found
        """
        mocker.patch.object(
            APIKey.objects, "get", side_effect=APIKey.DoesNotExist
        )

        with pytest.raises(AuthenticationFailed):
            auth_obj = TokenWithGetParamAuthentication()
            auth_obj.authenticate_credentials(key="")

    def test_authenticate_credentials_valid_key(self, mocker, api_key):
        """
        Test user and key are returned when key is authenticated
        """
        key = mocker.MagicMock(spec=APIKey, key=api_key)
        key.user.pk = 1
        mocker.patch.object(APIKey.objects, "get", return_value=key)

        auth_obj = TokenWithGetParamAuthentication()
        result = auth_obj.authenticate_credentials(key=api_key)

        assert type(result[0]) == CustomUser
        assert result[1] == key.key

    def test_cached_auth_database_calls(
        self, django_user_model, api_key, db, django_assert_num_queries
    ):
        """
        Test user and key are returned when key is authenticated
        """
        user = django_user_model.objects.create()
        api_key = APIKey.objects.create(user=user)

        # The first request should cause a DB hit
        with django_assert_num_queries(2):
            auth_obj = TokenWithGetParamAuthentication()
            auth_obj.authenticate_credentials(key=api_key.key)

        # The second should be cached
        with django_assert_num_queries(0):
            auth_obj = TokenWithGetParamAuthentication()
            auth_obj.authenticate_credentials(key=api_key.key)


class TestIsValidAPIUser:
    @pytest.mark.parametrize("is_authenticated", [True, False])
    def test_has_permission(self, is_authenticated, mocker):
        request = mocker.MagicMock()
        request.user = mocker.MagicMock(
            spec=CustomUser, is_authenticated=is_authenticated
        )
        perm_obj = IsValidAPIUser()
        assert perm_obj.has_permission(request, "view") is is_authenticated

    def test_has_permission_anonymous_user(self, mocker):
        # use anonymous user so AttributeError is raised attempting to get keys
        request = mocker.Mock()
        request.user = AnonymousUser()
        perm_obj = IsValidAPIUser()

        assert perm_obj.has_permission(request, "view") is False
