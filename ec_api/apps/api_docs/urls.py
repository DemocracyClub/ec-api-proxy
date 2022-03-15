from django.urls import path

from ec_api.apps.api_docs import views

urlpatterns = [
    path("", views.APIDocsHome.as_view(), name="api_docs"),
    path("concepts/", views.APIDocsConcepts.as_view(), name="api_concepts"),
    path(
        "endpoints/",
        views.APIEndpointsView.as_view(),
        name="api_docs_endpoints",
    ),
    path("notes/", views.APINotesView.as_view(), name="api_docs_notes"),
]
