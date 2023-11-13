from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware import Middleware


class ForwardedForMiddleware:
    def __init__(
        self,
        app,
    ):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            forwarded_for = (
                headers.get("x-forwarded-host", "").split(":")[0].encode()
            )
            if forwarded_for:
                for i, header in enumerate(scope["headers"]):
                    if header[0] == b"host":
                        scope["headers"].pop(i)
                scope["headers"].append((b"host", forwarded_for))
        await self.app(scope, receive, send)


class SimpleCORS:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_with_cors_headers(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("Access-Control-Allow-Origin", "*")

            await send(message)

        await self.app(scope, receive, send_with_cors_headers)
        return None


class APIGatewayAuthenticatorContextMiddleware:
    """
    Some app functions are behind an AWS API Gateway Authorizer.

    The Authorizer will control access to the Lambdas functions "behind" it,
    and will also insert context data about the authenticated user.

    We want to use this data when logging access, so this middleware parses the
    context in to a User model that can be used by functions.

    There are two other cases to consider:

    1. When we're on AWS Lambda but running an unauthenticated function.
       We don't know who the user is in this case, so we can just create a fake user
    2. When we're not on AWS Lambda, like when running tests or local dev.

    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        aws_event = scope.get("aws.event", {})
        authorizer_data = aws_event.get("requestContext", {}).get(
            "authorizer", {}
        )

        if authorizer_data:
            # We've been passed through an authorizer so we can create a User model
            api_key = authorizer_data["auth_token"]
        elif aws_event:
            # We're on AWS Lambda, but this isn't a function with an authorizer
            api_key = "unauthenticated_user"
        else:
            # We're not on AWS Lambda
            api_key = "direct_access"

        scope["api_user"] = api_key
        await self.app(scope, receive, send)


MIDDLEWARE = [
    Middleware(ForwardedForMiddleware),
    Middleware(SimpleCORS),
    Middleware(APIGatewayAuthenticatorContextMiddleware),
]
