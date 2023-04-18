"""
Consumes the devs.DC API and optionally cleans data for reuse

"""
import os
from json import JSONDecodeError

import requests
from starlette.requests import Request

session = requests.Session()

DC_API_TOKEN = os.environ.get("DC_API_TOKEN", None)
DC_API_URL = os.environ.get(
    "DC_API_URL", "https://developers.democracyclub.org.uk"
)


class DevsDCException(Exception):
    def __init__(self, response: requests.Response):
        try:
            self.message = response.json()
        except JSONDecodeError:
            self.message = {"error": "Unknown error"}
        self.status = response.status_code


class DCApiClient:
    def get_response_from_upstream(self, path, api_key, params=None):
        if not params:
            params = {}
        params["auth_token"] = api_key
        url = f"{DC_API_URL}/{path}"
        req = session.get(url, params=params)
        if req.status_code >= 400:
            raise DevsDCException(req)
        return req.json()

    def _get_raw_postcode_response(self, postcode, api_key):
        json = self.get_response_from_upstream(
            f"/api/v1/postcode/{postcode}", api_key
        )
        return json

    def _get_raw_uprn_response(self, uprn, api_key):
        json = self.get_response_from_upstream(
            f"/api/v1/address/{uprn}", api_key
        )
        return json

    def clean_candidates(self, candidates):
        for candidate in candidates:
            candidate["person"].pop("email", None)
            candidate["person"].pop("absolute_url", None)
            candidate["person"].pop("photo_url", None)
            candidate["person"].pop("leaflets", None)
        return candidates

    def clean_ballots(self, ballots):
        for ballot in ballots:
            ballot.pop("wcivf_url", None)
            ballot.pop("hustings", None)
            ballot.pop("ballot_url", None)
            if ballot["candidates_verified"]:
                ballot["candidates"] = self.clean_candidates(
                    ballot["candidates"]
                )
            else:
                ballot["candidates"] = []
        return ballots

    def clean_dates(self, request, raw_response):
        for date_obj in raw_response.get("dates", []):
            date_obj["ballots"] = self.clean_ballots(date_obj["ballots"])
        return raw_response

    def clean_addresses(self, request: Request, raw_response):
        for address in raw_response["addresses"]:
            uprn = address["url"].rstrip("/").split("/")[-1]
            address["url"] = str(request.url_for("address", uprn=uprn))
        return raw_response

    def clean_postcode_response(self, request, raw_response):
        raw_response = self.clean_dates(request, raw_response)
        raw_response = self.clean_addresses(request, raw_response)
        return raw_response

    def get_api_key(self, request: Request):
        return request.scope.get("api_user", DC_API_TOKEN)

    def clean_uprn_response(self, request, raw_response):
        # At the moment, cleaning a UPRN response is the same as a postcode
        # response
        raw_response = self.clean_postcode_response(request, raw_response)
        return raw_response

    def get_postcode_response(self, request, postcode):
        raw_response = self._get_raw_postcode_response(
            postcode, api_key=self.get_api_key(request)
        )
        return self.clean_postcode_response(request, raw_response)

    def get_uprn_response(self, request, uprn):
        raw_response = self._get_raw_uprn_response(
            uprn, api_key=self.get_api_key(request)
        )
        return self.clean_uprn_response(request, raw_response)


class ResponseBuilderApiClient(DCApiClient):
    builder = None

    def get_response_from_upstream(self, path, params=None):
        raise NotImplementedError("This method should not ever be called")

    def _get_raw_postcode_response(self, postcode):
        return self.builder.response

    def _get_raw_uprn_response(self, uprn):
        return self.builder.response
