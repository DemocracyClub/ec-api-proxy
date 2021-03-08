import pytest

from api_proxy.auth import IsValidAPIUser


@pytest.fixture
def authorized_client(mocker, client):
    """
    Mocks API permission class check to return True and returns a client object
    to be used in view tests
    """
    mocker.patch.object(IsValidAPIUser, "has_permission", return_value=True)
    return client
