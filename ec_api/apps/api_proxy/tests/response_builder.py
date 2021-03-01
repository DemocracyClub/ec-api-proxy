"""
A set of tools for creating responses from the DC aggregator API.

Used for testing.

"""
import json


class BaseResponse:
    def __init__(self):
        self.options = {}
        self._response = self.get_response()

    def build_response(self):
        raise NotImplementedError

    def get_response(self):
        raise NotImplementedError

    @property
    def as_json(self):
        return json.dumps(self.response)

    @property
    def response(self):
        self.build_response()
        return self._response


class CouncilContactDetailsMixin:
    options = {}

    @property
    def get_electoral_services(self):
        if self.options.get("split_council"):
            return None

        return {
            "council_id": "E09000033",
            "name": "City of Westminster",
            "nation": "England",
            "email": "electoralservices@westminster.gov.uk",
            "phone": "020 7641 2730",
            "website": "http://www.westminster.gov.uk/",
            "postcode": "WC2N 5HR",
            "address": "Electoral Registration Officer\nWestminster City Council\n2nd Floor, City Hall\n5 Strand",
        }

    @property
    def get_registration(self):
        if self.options.get("split_council"):
            return None

        return {
            "council_id": "E09000033",
            "name": "City of Westminster",
            "nation": "England",
            "email": "electoralservices@westminster.gov.uk",
            "phone": "020 7641 2730",
            "website": "http://www.westminster.gov.uk/",
            "postcode": "WC2N 5HR",
            "address": "Electoral Registration Officer\nWestminster City Council\n2nd Floor, City Hall\n5 Strand",
        }


class PostcodeResponse(CouncilContactDetailsMixin, BaseResponse):
    def get_response(self):
        return {
            "address_picker": self.get_address_picker,
            "addresses": self.get_addresses,
            "dates": self.get_dates,
            "postcode_location": self.get_postcode_location,
            "electoral_services": self.get_electoral_services,
            "registration": self.get_registration,
        }

    @property
    def get_addresses(self):
        return []

    @property
    def get_dates(self):
        return []

    @property
    def get_address_picker(self):
        return getattr(self, "address_picker", False)

    def with_addresses(self, number=10):
        self.address_picker = True
        # del council contacts

    @property
    def get_postcode_location(self):
        return {
            "type": "Feature",
            "properties": None,
            "geometry": {
                "type": "Point",
                "coordinates": [-0.13447605, 51.489488200000004],
            },
        }

    def with_split_over_councils_postcode(self):
        """
        This postcode is split over two or more councils
        """
        self.options["split_council"] = True
        return self

    def build_response(self):
        self._response = self.get_response()
        self._response["addresses"] = self.get_addresses
        self._response["dates"] = self.get_dates
        self._response["address_picker"] = self.get_address_picker
        if not self.get_address_picker:
            assert not self.get_addresses
