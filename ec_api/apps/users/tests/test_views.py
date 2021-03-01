import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.forms import LoginForm

from users.tests.factories import UserFactory
from users.views import RegisterView, LoginView
from pytest_django.asserts import assertContains

User = get_user_model()


class TestContextMixin:
    @pytest.fixture
    def view_obj(self):
        """
        Init an instance of RegisterView with a User object
        """
        view = RegisterView()
        view.object = User()
        return view

    @pytest.mark.parametrize(
        "url, expected",
        [
            ("/users/register/", False),
            ("/users/register/?success", True),
        ],
    )
    def test_get_context_data_success(self, url, expected, rf, view_obj):
        request = rf.get(url)
        view_obj.setup(request=request)
        context = view_obj.get_context_data()

        assert "success" in context
        assert context["success"] == expected

    def get_success_url(self, view_obj):
        assert view_obj.get_success_url() == ".?success"


class TestLoginView:
    @pytest.fixture
    def view_obj(self, rf):
        """
        Init an instance of RegisterView with a User object
        """
        view = LoginView()
        view.object = User()
        view.setup(request=rf.get("/users/login/"))
        return view

    def test_form_valid_user_found(self, view_obj, mocker):
        user = User()
        mocker.patch.object(User.objects, "get", return_value=user)
        mocker.patch.object(view_obj, "send_login_url")
        form = LoginForm()
        form.cleaned_data = {"email": "email@example.com"}

        response = view_obj.form_valid(form)

        User.objects.get.assert_called_once_with(email="email@example.com")
        view_obj.send_login_url.assert_called_once_with(user=user)
        assert response.status_code == 302
        assert response.url == ".?success"

    def test_form_valid_user_not_found(self, view_obj, mocker):
        mocker.patch.object(User.objects, "get", side_effect=User.DoesNotExist)
        mocker.patch.object(view_obj, "send_login_url")
        form = LoginForm()
        form.cleaned_data = {"email": "notregistered@example.com"}

        response = view_obj.form_valid(form)

        User.objects.get.assert_called_once_with(
            email="notregistered@example.com"
        )
        view_obj.send_login_url.assert_not_called()
        assert response.status_code == 302
        assert response.url == ".?success"

    def test_send_login_url(self, view_obj, mocker):
        mocker.patch("users.views.get_query_string")
        user = mocker.MagicMock(spec=User)
        view_obj.send_login_url(user)

        user.email_user.assert_called_once()


class TestAuthenticateView:
    @pytest.fixture
    def url(self):
        return reverse("users:authenticate")

    def tests_get_redirects_to_error(self, client, url):
        response = client.get(url, follow=True)

        assert response.wsgi_request.path == "/users/authenticate/error/"
        assertContains(response, "<h1>Something went wrong</h1>")

    @pytest.mark.django_db
    def test_get_logs_in_user(self, client, mocker, url):
        user = UserFactory()
        mocker.patch("users.views.get_user", return_value=user)
        response = client.get(url)

        assert response.status_code == 200
        assert response.wsgi_request.user is user
        assertContains(response, "<h1>Authenticated</h1>")
