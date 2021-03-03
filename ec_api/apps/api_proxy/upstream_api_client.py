"""
Consumes the devs.DC API and optionally cleans data for reuse

"""
import requests
from django.conf import settings


class DCApiClient:
    def get_response_from_upstream(self, path, params=None):
        if not params:
            params = {}
        params["auth_token"] = settings.DC_API_TOKEN
        url = f"{settings.DC_API_URL}/{path}"
        req = requests.get(url, params=params)
        req.raise_for_status()
        return req.json()

    def _get_raw_postcode_response(self, postcode):
        # TODO: Validate postcode
        # TODO: clean emails

        json = self.get_response_from_upstream(f"/api/v1/postcode/{postcode}")
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

    def clean_postcode_response(self, raw_response):
        raw_response = self.clean_dates(raw_response)
        return raw_response

    def get_postcode_response(self, postcode):
        raw_response = self._get_raw_postcode_response(postcode)
        return self.clean_postcode_response(raw_response)


class ResponseBuilderApiClient(DCApiClient):
    builder = None

    def get_response_from_upstream(self, path, params=None):
        raise NotImplementedError("This method should not ever be called")

    def _get_raw_postcode_response(self, postcode):
        return self.builder.response
