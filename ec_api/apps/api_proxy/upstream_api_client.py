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

    def get_postcode_response(self, postcode):
        # TODO: Validate postcode
        # TODO: clean emails

        json = self.get_response_from_upstream(f"/api/v1/postcode/{postcode}")
        return json


class ResponseBuilderApiClient(DCApiClient):
    builder = None

    def get_response_from_upstream(self, path, params=None):
        raise NotImplementedError("This method should not ever be called")

    def get_postcode_response(self, postcode):
        return self.builder.response
