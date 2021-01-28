from django.urls import path

from ec_api.apps.frontend import views

urlpatterns = [
    path("", views.HomePageView.as_view()),
]
