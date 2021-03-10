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
        mocker.patch.object(APIKey.objects, "get", return_value=key)

        auth_obj = TokenWithGetParamAuthentication()
        result = auth_obj.authenticate_credentials(key=api_key)

        assert result == (key.user, key)


class TestIsValidAPIUser:
    @pytest.mark.parametrize("exists", [True, False])
    def test_has_permission(self, exists, mocker):
        request = mocker.MagicMock()
        request.user = mocker.MagicMock(spec=CustomUser)
        request.user.api_keys.exists.return_value = exists
        perm_obj = IsValidAPIUser()

        assert perm_obj.has_permission(request, "view") is exists
        request.user.api_keys.exists.assert_called_once()

    def test_has_permission_anonymous_user(self, mocker):
        # use anonymous user so AttributeError is raised attempting to get keys
        request = mocker.Mock()
        request.user = AnonymousUser()
        perm_obj = IsValidAPIUser()

        assert perm_obj.has_permission(request, "view") is False
