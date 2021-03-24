from django.urls import path

from ec_api.apps.api_docs import views

urlpatterns = [
    path("", views.APIDocsHome.as_view(), name="api_docs"),
]
