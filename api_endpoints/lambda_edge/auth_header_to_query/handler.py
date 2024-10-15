from urllib.parse import parse_qs, urlencode


def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]

    """
    This code is run between a request from the web and that request
    being passed on to CloudFront:

    Request -> function -> CloudFront -> Origin

    We use it to convert the `Authorization` header into a
    query string parameter.

    This is due to AWS API Gateway not being able to support
    more than one authentication method using OR.

    That is, you can add header and query string authentication methods, but
    they are ANDed together meaning you need to supply both.

    This function allows us to accept either by converting one method to using
    the other method.

    """

    # Check if the header exists
    token_header = request["headers"].get("authorization")
    if not token_header:
        # If not, return early. Nothing to be done here
        return request

    # Parse request querystring to get dictionary/json
    params = {k: v[0] for k, v in parse_qs(request["querystring"]).items()}
    # The header value is in the format of:
    # {lower_case_header_name: [{"key": "Title_Case_Header_Name", "value": "value"}]}
    # And the authorization header value is "Token api_key"
    token = token_header[0]["value"].split(" ")[-1]
    params["token"] = token
    request["querystring"] = urlencode(params)

    return request
