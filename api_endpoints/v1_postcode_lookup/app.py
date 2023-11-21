import os

from dc_logging_client import DCWidePostcodeLoggingClient
from mangum import Mangum
from middleware import MIDDLEWARE
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from upstream_api_client import DCApiClient, DevsDCException
from utils import init_sentry

client = DCApiClient()

init_sentry()

if logger_arn := os.environ.get("LOGGER_ARN"):
    POSTCODE_LOGGER = DCWidePostcodeLoggingClient(function_arn=logger_arn)
else:
    POSTCODE_LOGGER = DCWidePostcodeLoggingClient(fake=True)


def get_postcode_response(request: Request):
    postcode = request.path_params["postcode"]

    # Log this request
    entry = POSTCODE_LOGGER.entry_class(
        postcode=postcode,
        dc_product=POSTCODE_LOGGER.dc_product.ec_api,
        calls_devs_dc_api=True,
        api_key=request.scope["api_user"],
    )
    POSTCODE_LOGGER.log(entry)

    try:
        response = client.get_postcode_response(request, postcode)
    except DevsDCException as error:
        return JSONResponse(error.message, error.status)
    return JSONResponse(response)


def get_address_response(request: Request):
    uprn = request.path_params["uprn"]
    try:
        response = client.get_uprn_response(request, uprn)
    except DevsDCException as error:
        return JSONResponse(error.message, error.status)
    return JSONResponse(response)


routes = [
    Route(
        "/api/v1/postcode/{postcode}/",
        get_postcode_response,
        methods=["GET"],
        name="postcode",
    ),
    Route(
        "/api/v1/address/{uprn}/",
        get_address_response,
        methods=["GET"],
        name="address",
    ),
]

app = Starlette(
    debug=os.environ.get("DEBUG", False), routes=routes, middleware=MIDDLEWARE
)

handler = Mangum(app, lifespan="off")
