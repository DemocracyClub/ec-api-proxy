from django.urls import path
from api_proxy import views

urlpatterns = [
    path("v1/postcode/<postcode>", views.PostcodeView.as_view()),
]
