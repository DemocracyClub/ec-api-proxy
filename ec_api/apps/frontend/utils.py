import os


def get_domain(request):
    return os.environ.get("APP_DOMAIN", request.META.get("HTTP_HOST"))
