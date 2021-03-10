import pytest

from api_proxy.tests.response_builder import (
    PostcodeResponse,
    SingleBallotResponse,
)
from api_proxy.upstream_api_client import ResponseBuilderApiClient


@pytest.fixture
def response_client(settings):
    rc = ResponseBuilderApiClient()
    settings.API_CLIENT_CLASS = rc
    return rc


@pytest.fixture
def postcode_response(response_client) -> PostcodeResponse:
    response_client.builder = PostcodeResponse()
    return response_client.builder


def test_get_postcode_split_over_councils(authorized_client, postcode_response):
    postcode_response.with_split_over_councils_postcode()
    resp_json = authorized_client.get("/api/v1/postcode/GL51NA").json()

    assert resp_json["electoral_services"] is None
    assert resp_json["registration"] is None


def test_get_postcode_no_data_with_contacts(
    authorized_client, postcode_response
):
    resp_json = authorized_client.get("/api/v1/postcode/GL51NA").json()
    assert type(resp_json["electoral_services"]) is dict
    assert resp_json["address_picker"] is False


def test_email_not_in_candiate_response(authorized_client, postcode_response):
    ballot = SingleBallotResponse()
    ballot.with_random_candidates()
    postcode_response.with_ballot_on_date("2021-05-06", ballot)
    resp_json = authorized_client.get("/api/v1/postcode/GL51NA").json()
    candidate = resp_json["dates"][0]["ballots"][0]["candidates"][0]
    assert candidate["list_position"] is None
    with pytest.raises(KeyError):
        assert candidate["person"]["email"]
    with pytest.raises(KeyError):
        assert candidate["person"]["absolute_url"]
    with pytest.raises(KeyError):
        assert candidate["person"]["photo_url"]
