"""
Test the the reponse builder does what we want it to do

"""
from api_proxy.tests.response_builder import PostcodeResponse


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
    assert builder.response == {
        "address_picker": True,
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
        "electoral_services": None,
        "registration": None,
    }
