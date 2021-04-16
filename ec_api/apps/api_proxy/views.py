from django.conf import settings
from django.utils.module_loading import import_string
from requests import HTTPError
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from rest_framework.response import Response
from api_proxy.auth import IsValidAPIUser, TokenWithGetParamAuthentication

from api_proxy.upstream_api_client import ResponseBuilderApiClient


def get_upstream_client(request):
    """
    Allow pluggable clients to get some JSON back to the view.

    This is to make mocking / testing easier - we use ResponseBuilder in tests
    to configure exact responses that this view should return.

    In production we make an HTTP connection to the upstream server and return
    JSON from that.
    """
    DEFAULT_CLIENT = "api_proxy.upstream_api_client.DCApiClient"
    client_class = getattr(settings, "API_CLIENT_CLASS", DEFAULT_CLIENT)
    if isinstance(client_class, ResponseBuilderApiClient):
        return client_class
    if isinstance(client_class, str):
        return import_string(client_class)(request)

    raise ValueError("Invalid value for API_CLIENT_CLASS")


class BaseAuthenticatedAPIView(APIView):
    authentication_classes = [TokenWithGetParamAuthentication]
    permission_classes = [IsValidAPIUser]


class PostcodeView(BaseAuthenticatedAPIView):
    def get(self, request, postcode, format=None):
        try:
            response = get_upstream_client(request).get_postcode_response(
                postcode
            )
            return Response(response)
        except HTTPError as requests_exception:
            if str(requests_exception.response.status_code) == "400":
                raise ParseError(detail=requests_exception.response.json())
            else:
                raise requests_exception


class UPRNView(BaseAuthenticatedAPIView):
    def get(self, request, uprn, format=None):
        try:
            response = get_upstream_client(request).get_uprn_response(uprn)
            return Response(response)
        except HTTPError as requests_exception:
            if str(requests_exception.response.status_code) == "400":
                raise ParseError(detail=requests_exception.response.json())
            else:
                raise (requests_exception)
