from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("users.urls")),
    path("", include("frontend.urls")),
    path("docs/", include("api_docs.urls")),
    path("api/", include("api_proxy.urls")),
]
