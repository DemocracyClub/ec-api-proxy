"""
A set of tools for creating responses from the DC aggregator API.

Used for testing.

"""
import datetime
import json
from random import randrange

from faker import Faker
from uk_election_ids.election_ids import IdBuilder

from api_proxy.tests.name_factory import make_ward_name, make_org_name


class BaseResponse:
    def __init__(self):
        self.options = {}
        self._response = self.get_initial_response()

    def build_response(self):
        raise NotImplementedError

    def get_initial_response(self):
        raise NotImplementedError

    @property
    def as_json(self):
        return json.dumps(self.response)

    def _build_all_responses(self):
        """
        Responses can contain sub-responses - make sure that all of them are
        built out when we call `response` on the parent
        :return:
        """
        self.build_response()

        def build(obj):
            if isinstance(obj, BaseResponse):
                obj = obj.response
            if type(obj) == list:
                for i, item in enumerate(obj):
                    item = build(item)
                    obj[i] = item
            if type(obj) is dict:
                for key, value in obj.items():
                    obj[key] = build(value)
            return obj

        self._response = build(self._response)

    @property
    def response(self):
        self._build_all_responses()
        return self._response


class SingleCandidateResponse(BaseResponse):
    def get_initial_response(self):
        fake_data = Faker()
        person_id = fake_data.unique.random_int()
        return {
            "list_position": None,
            "party": {
                "party_id": "party:52",
                "party_name": "Conservative and Unionist Party",
            },
            "person": {
                "ynr_id": person_id,
                "name": fake_data.name(),
                "absolute_url": f"https://whocanivotefor.co.uk/person/{person_id}/chris-nelson",
                "email": fake_data.ascii_company_email(),
                "photo_url": "https://static-candidates.democracyclub.org.uk/media/cache/49/ed/49ed2227043044a2c44405f9ae1b6795.jpg",
            },
        }

    def build_response(self):
        return self.get_initial_response()


class SingleBallotResponse(BaseResponse):
    def get_initial_response(self):
        return {"ballot_paper_id": "local.stroud.2021-05-06", "candidates": []}

    def build_response(self):
        return self.get_initial_response()

    def with_random_ballot_paper_id(self):
        ballot = (
            IdBuilder("local", datetime.date(2018, 5, 3))
            .with_organisation(make_org_name())
            .with_division(make_ward_name())
        )
        self._response["ballot_paper_id"] = ballot.ballot_id
        return self

    def with_random_candidates(self, count=1):
        for i in range(count):
            self._response["candidates"].append(SingleCandidateResponse())


class BallotsResponse(BaseResponse):
    _ballots = []

    def get_initial_response(self):
        return self._ballots

    def with_ballot(self, ballot):
        self._ballots.append(ballot)

    def build_response(self):
        return self.get_initial_response()


class SingleAddressResponse(BaseResponse):
    def get_initial_response(self):
        fake_data = Faker(["en_GB"])
        uprn = fake_data.random_number(digits=11)
        return {
            "address": fake_data.address(),
            "postcode": fake_data.postcode(),
            "slug": uprn,
            "url": f"https://developers.democracyclub.org.uk/api/v1/address/{uprn}/",
        }

    def build_response(self):
        return self.get_initial_response()


class CouncilContactDetailsMixin:
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


class DatesMixin:
    _dates = []

    @property
    def get_dates(self):
        return self._dates

    def get_date_object(self, date):
        return {
            "date": date,
            "polling_station": {
                # TODO: polling station builder here
                "polling_station_known": False,
                "custom_finder": None,
                "report_problem_url": None,
                "station": None,
            },
            "notifications": [],
            "ballots": BallotsResponse(),
        }

    def with_future_dates(self, count=1, date_list: list = None):
        if date_list:
            assert isinstance(date_list, list)
        assert not self._dates, "Dates already set"
        assert not self.options.get("split_council"), (
            "No dates shown for split " "postcodes"
        )
        from_date = datetime.date.today()
        if not date_list:
            date_list = []
            for i in range(count):
                random_days_in_future = randrange(5, 30)
                election_date = from_date + datetime.timedelta(
                    days=random_days_in_future
                )
                date_list.append(election_date)
                from_date = election_date

        dates = []
        for date in date_list:
            dates.append(self.get_date_object(date))

        self._dates = dates
        return self

    def with_ballot_on_date(self, date, ballot):
        if not self.get_dates:
            self.with_future_dates(date_list=[date])
        assert date in [d["date"] for d in self.get_dates]
        for date_obj in self.get_dates:
            if date_obj["date"] == date:
                date_obj["ballots"].with_ballot(ballot)
        return self


class PostcodeResponse(DatesMixin, CouncilContactDetailsMixin, BaseResponse):
    def get_initial_response(self):
        return {
            "address_picker": self.get_address_picker,
            "addresses": [],
            "dates": self.get_dates,
            "postcode_location": self.get_postcode_location,
            "electoral_services": self.get_electoral_services,
            "registration": self.get_registration,
        }

    @property
    def get_address_picker(self):
        return getattr(self, "address_picker", False)

    def with_addresses(self, number=10):
        self.address_picker = True
        self._response["electoral_services"] = None
        self._response["registration"] = None
        self._response["addresses"] = [
            SingleAddressResponse() for i in range(number)
        ]
        return self

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
        self.with_addresses(5)
        return self

    def build_response(self):
        self._response["dates"] = self.get_dates
        self._response["address_picker"] = self.get_address_picker
        if not self.get_address_picker:
            assert not self._response["addresses"]
