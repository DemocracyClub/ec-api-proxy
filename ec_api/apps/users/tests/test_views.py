import pytest
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic.edit import DeleteView
from pytest_django.asserts import assertContains
from users.forms import APIKeyForm, LoginForm
from users.tests.factories import APIKeyFactory, UserFactory
from users.views import (
    DeleteAPIKeyView,
    LoginView,
    ProfileView,
    RefreshAPIKeyView,
)

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

    def test_send_login_url(self, view_obj, mocker):
        mocker.patch("users.views.get_query_string")
        user = mocker.MagicMock(spec=User)
        view_obj.send_login_url(user)

        user.email_user.assert_called_once()

    def get_success_url(self, view_obj):
        assert view_obj.get_success_url() == reverse("users:login")


class TestAuthenticateView:
    @pytest.fixture
    def url(self):
        return reverse("users:authenticate")

    def tests_get_redirects_to_error(self, client, url):
        response = client.get(url, follow=True)

        assert response.status_code == 200
        assert response.wsgi_request.path == url
        assert response.wsgi_request.user.is_authenticated is False
        assertContains(response, "<h1>Something went wrong</h1>")

    @pytest.mark.django_db
    def test_get_logs_in_user_redirects_to_edit_profile(
        self, client, mocker, url
    ):
        user = UserFactory()
        mocker.patch("users.views.get_user", return_value=user)
        response = client.get(url, follow=True)

        assert response.wsgi_request.user == user
        assertContains(response, "<h1>Update Profile</h1>")

    @pytest.mark.django_db
    def test_get_logs_in_user_with_name_redirects_to_profile(
        self, client, mocker, url
    ):
        user = UserFactory(name="Foo Bar")
        mocker.patch("users.views.get_user", return_value=user)
        response = client.get(url, follow=True)

        assert response.wsgi_request.user == user
        assertContains(response, "Foo Bar")


class TestProfileView:
    @pytest.fixture
    def view_obj(self, rf, mocker):
        request = rf.get(reverse("users:profile"))
        request.user = mocker.MagicMock(spec=User)
        obj = ProfileView()
        obj.setup(request=request)
        return obj

    def test_get_success_url(self, view_obj):
        assert view_obj.get_success_url() == reverse("users:profile")

    def test_get_context_data(self, view_obj):
        context = view_obj.get_context_data()

        assert "api_keys" in context
        view_obj.request.user.api_keys.all.assert_called_once()

    def test_form_valid(self, view_obj, mocker):
        form = mocker.MagicMock(spec=APIKeyForm)
        mocker.patch.object(messages, "success")
        result = view_obj.form_valid(form=form)

        form.save.assert_called_once_with(commit=False)
        assert form.save.return_value.user == view_obj.request.user
        form.save.return_value.save.assert_called_once()
        assert result.status_code == 302
        assert result.url == reverse("users:profile")
        messages.success.assert_called_once()

    def test_must_be_logged_in(self, client):
        response = client.get(reverse("users:profile"))
        assert response.status_code == 302
        assert response.url == reverse("users:login")


class TestDeleteAPIKeyView:
    @pytest.fixture
    def view_obj(self, rf):
        url = reverse("users:delete-key", kwargs={"pk": 1})
        request = rf.get(url)
        obj = DeleteAPIKeyView()
        obj.setup(request=request)
        return obj

    @pytest.mark.django_db
    def test_get_queryset_limited_to_users_keys(self, view_obj):
        user = UserFactory()
        APIKeyFactory.create_batch(size=5, user=user)

        another_users_key = APIKeyFactory()
        view_obj.request.user = user

        result = view_obj.get_queryset()
        assert list(result) == list(user.api_keys.all())
        assert another_users_key not in result

    def test_get_success_url(self, view_obj):
        result = view_obj.get_success_url()
        assert result == reverse("users:profile")

    def test_delete(self, view_obj, mocker):
        # give the view an object
        view_obj.object = APIKeyFactory.build(name="Test")
        # patch super call
        mocker.patch.object(DeleteView, "delete")
        # patch messages call
        mocker.patch.object(messages, "success")

        view_obj.delete(request=view_obj.request)
        DeleteView.delete.assert_called_once()
        messages.success.assert_called_once()


class TestRefreshAPIKeyView:
    def test_post(self, rf, mocker):
        key = APIKeyFactory.build(pk=1)
        view = RefreshAPIKeyView()
        view.request = rf.post(key.get_absolute_refresh_url())
        mocker.patch.object(key, "refresh_key")
        mocker.patch.object(view, "get_object", return_value=key)
        mocker.patch.object(messages, "success", return_value=key)

        response = view.post(view.request)

        key.refresh_key.assert_called_once()
        view.get_object.assert_called_once()
        assert response.status_code == 302
        assert response.url == reverse("users:profile")
        messages.success.assert_called_once()
