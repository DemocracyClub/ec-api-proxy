"""
Test the the reponse builder does what we want it to do

"""
import pytest

from api_proxy.tests.response_builder import (
    PostcodeResponse,
    SingleBallotResponse,
)


def get_by_date_from_response(response, date):
    for date_obj in response.get("dates", []):
        if date_obj.get("date") == date:
            return date_obj


def test_postcode_response():
    builder = PostcodeResponse()
    assert builder.response == {
        "address_picker": False,
        "addresses": [],
        "dates": [],
        "postcode_location": {
            "type": "Feature",
            "properties": None,
            "geometry": {
                "type": "Point",
                "coordinates": [-0.13447605, 51.489488200000004],
            },
        },
        "electoral_services": {
            "council_id": "E09000033",
            "name": "City of Westminster",
            "nation": "England",
            "email": "electoralservices@westminster.gov.uk",
            "phone": "020 7641 2730",
            "website": "http://www.westminster.gov.uk/",
            "postcode": "WC2N 5HR",
            "address": "Electoral Registration Officer\nWestminster City Council\n2nd Floor, City Hall\n5 Strand",
        },
        "registration": {
            "council_id": "E09000033",
            "name": "City of Westminster",
            "nation": "England",
            "email": "electoralservices@westminster.gov.uk",
            "phone": "020 7641 2730",
            "website": "http://www.westminster.gov.uk/",
            "postcode": "WC2N 5HR",
            "address": "Electoral Registration Officer\nWestminster City Council\n2nd Floor, City Hall\n5 Strand",
        },
    }


def test_postcode_split_over_councils():
    builder = PostcodeResponse().with_split_over_councils_postcode()
    assert len(builder.response["addresses"]) == 5
    assert list(builder.response.keys()) == [
        "address_picker",
        "addresses",
        "dates",
        "postcode_location",
        "electoral_services",
        "registration",
    ]


def test_with_two_future_dates():
    builder = PostcodeResponse().with_future_dates(count=2)
    assert len(builder.response["dates"]) == 2
    assert "date" in builder.response["dates"][0]


def test_with_two_given_dates():
    builder = PostcodeResponse().with_future_dates(
        date_list=["2019-12-12", "2021-05-06"]
    )
    assert len(builder.response["dates"]) == 2
    assert builder.response["dates"][0]["date"] == "2019-12-12"


def test_ballots_for_date():
    builder = PostcodeResponse().with_future_dates(
        date_list=["2019-12-12", "2021-05-06"]
    )
    date = builder.response["dates"][0]
    assert date["ballots"] == []


def test_split_postcode_validation():
    builder = PostcodeResponse().with_split_over_councils_postcode()
    with pytest.raises(AssertionError) as error:
        builder.with_future_dates()
    assert str(error.value) == "No dates shown for split postcodes"


def test_set_dates_twice():
    builder = PostcodeResponse().with_future_dates(2)
    with pytest.raises(AssertionError) as error:
        builder.with_future_dates(1)
    assert str(error.value) == "Dates already set"


def test_build_ballot_response():
    builder = PostcodeResponse().with_future_dates(date_list=["2019-12-12"])
    ballot = SingleBallotResponse()
    ballot.with_random_ballot_paper_id()
    ballot.with_random_candidates(4)
    builder.with_ballot_on_date("2019-12-12", ballot)
    date_obj = get_by_date_from_response(builder.response, "2019-12-12")
    assert date_obj["ballots"][0]["ballot_paper_id"].startswith("local.")
    assert list(date_obj["ballots"][0]["candidates"][0].keys()) == [
        "list_position",
        "party",
        "person",
    ]
