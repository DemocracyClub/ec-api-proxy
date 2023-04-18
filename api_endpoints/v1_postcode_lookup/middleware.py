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


MIDDLEWARE = [
    Middleware(ForwardedForMiddleware),
    Middleware(SimpleCORS),
]
