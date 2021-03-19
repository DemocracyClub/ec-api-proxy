from django.urls import path, include
from api_proxy import views

api_v1_urlpatterns = [
    path(
        "postcode/<postcode>/",
        views.PostcodeView.as_view(),
        name="postcode_view",
    ),
    path("address/<uprn>/", views.UPRNView.as_view(), name="uprn_view"),
]


urlpatterns = [path("v1/", include((api_v1_urlpatterns, "v1")))]
