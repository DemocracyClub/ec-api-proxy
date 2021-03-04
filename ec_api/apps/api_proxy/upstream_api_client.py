"""
Consumes the devs.DC API and optionally cleans data for reuse

"""
import requests
from django.conf import settings
from rest_framework.reverse import reverse


class DCApiClient:
    def __init__(self, request):
        self.request = request

    def get_response_from_upstream(self, path, params=None):
        if not params:
            params = {}
        params["auth_token"] = settings.DC_API_TOKEN
        url = f"{settings.DC_API_URL}/{path}"
        req = requests.get(url, params=params)
        req.raise_for_status()
        return req.json()

    def _get_raw_postcode_response(self, postcode):
        json = self.get_response_from_upstream(f"/api/v1/postcode/{postcode}")
        return json

    def _get_raw_uprn_response(self, uprn):
        json = self.get_response_from_upstream(f"/api/v1/address/{uprn}")
        return json

    def clean_candidates(self, candidates):
        for candidate in candidates:
            candidate["person"].pop("email")
            candidate["person"].pop("absolute_url")
            candidate["person"].pop("photo_url")
        return candidates

    def clean_ballots(self, ballots):
        for ballot in ballots:
            ballot.pop("wcivf_url", None)
            ballot.pop("ballot_url", None)
            ballot["candidates"] = self.clean_candidates(ballot["candidates"])
        return ballots

    def clean_dates(self, raw_response):
        for date_obj in raw_response.get("dates", []):
            date_obj["ballots"] = self.clean_ballots(date_obj["ballots"])
        return raw_response

    def clean_addresses(self, raw_response):
        for address in raw_response["addresses"]:
            uprn = address["url"].rstrip("/").split("/")[-1]
            address["url"] = reverse(
                "v1:uprn_view", kwargs={"uprn": uprn}, request=self.request
            )
        return raw_response

    def clean_postcode_response(self, raw_response):
        raw_response = self.clean_dates(raw_response)
        raw_response = self.clean_addresses(raw_response)
        return raw_response

    def clean_uprn_response(self, raw_response):
        # At the moment, cleaning a UPRN response is the same as a postcode
        # response
        raw_response = self.clean_postcode_response(raw_response)
        return raw_response

    def get_postcode_response(self, postcode):
        raw_response = self._get_raw_postcode_response(postcode)
        return self.clean_postcode_response(raw_response)

    def get_uprn_response(self, uprn):
        raw_response = self._get_raw_uprn_response(uprn)
        return self.clean_uprn_response(raw_response)


class ResponseBuilderApiClient(DCApiClient):
    builder = None

    def get_response_from_upstream(self, path, params=None):
        raise NotImplementedError("This method should not ever be called")

    def _get_raw_postcode_response(self, postcode):
        return self.builder.response

    def _get_raw_uprn_response(self, uprn):
        return self.builder.response
