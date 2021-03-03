import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.forms import LoginForm

from users.tests.factories import UserFactory
from users.views import LoginView
from pytest_django.asserts import assertContains

User = get_user_model()


class TestLoginView:
    @pytest.fixture
    def view_obj(self, rf):
        """
        Init an instance of LoginView with a User object
        """
        view = LoginView()
        view.object = User()
        view.setup(request=rf.get("/users/login/"))
        return view

    def test_form_valid_created_user(self, view_obj, mocker):
        user = mocker.MagicMock(spec=User)
        mocker.patch.object(
            User.objects, "get_or_create", return_value=(user, True)
        )
        mocker.patch.object(view_obj, "send_login_url")
        form = LoginForm()
        form.cleaned_data = {"email": "email@example.com"}

        response = view_obj.form_valid(form)

        User.objects.get_or_create.assert_called_once_with(
            email="email@example.com"
        )
        user.set_unusable_password.assert_called_once()
        user.save.assert_called_once()
        view_obj.send_login_url.assert_called_once_with(user=user)
        assert response.status_code == 302
        assert response.url == ".?success"

    def test_form_valid_existing_user(self, view_obj, mocker):
        user = mocker.MagicMock(spec=User)
        mocker.patch.object(
            User.objects, "get_or_create", return_value=(user, False)
        )
        mocker.patch.object(view_obj, "send_login_url")
        form = LoginForm()
        form.cleaned_data = {"email": "email@example.com"}

        response = view_obj.form_valid(form)

        User.objects.get_or_create.assert_called_once_with(
            email="email@example.com"
        )
        user.set_unusable_password.assert_not_called()
        user.save.assert_not_called()
        view_obj.send_login_url.assert_called_once_with(user=user)
        assert response.status_code == 302
        assert response.url == ".?success"

    def test_send_login_url(self, view_obj, mocker):
        mocker.patch("users.views.get_query_string")
        user = mocker.MagicMock(spec=User)
        view_obj.send_login_url(user)

        user.email_user.assert_called_once()

    @pytest.mark.parametrize(
        "url, expected",
        [
            ("/users/login/", False),
            ("/users/login/?success", True),
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
