import pytest

from api_proxy.tests.response_builder import PostcodeResponse
from api_proxy.upstream_api_client import ResponseBuilderApiClient


@pytest.fixture
def response_client(settings):
    rc = ResponseBuilderApiClient()
    settings.API_CLIENT_CLASS = rc
    return rc


@pytest.fixture
def postcode_response(response_client):
    response_client.builder = PostcodeResponse()
    return response_client


def test_get_postcode_split_over_councils(client, postcode_response):
    postcode_response.builder.with_split_over_councils_postcode()
    resp_json = client.get("/api/v1/postcode/GL51NA").json()
    assert resp_json["electoral_services"] is None
    assert resp_json["registration"] is None


def test_get_postcode_no_data_with_contacts(client, postcode_response):
    resp_json = client.get("/api/v1/postcode/GL51NA").json()
    assert type(resp_json["electoral_services"]) is dict
    assert resp_json["address_picker"] is False
