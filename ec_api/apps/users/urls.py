from django.urls import path
from django.contrib.auth import views as auth_views

from users import views

app_name = "users"
urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "authenticate/", views.AuthenticateView.as_view(), name="authenticate"
    ),
    path(
        "authenticate/error/",
        views.AuthenticateErrorView.as_view(),
        name="authenticate-error",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
]
