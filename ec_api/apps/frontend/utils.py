import os


def get_domain(request):
    return os.environ.get("DOMAIN", request.META.get("HTTP_HOST"))
