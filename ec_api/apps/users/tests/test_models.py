import pytest

from django.urls import reverse

from users.tests.factories import APIKeyFactory


class TestAPIKeyModel:
    @pytest.mark.django_db
    def test_refresh_key(self):
        api_key = APIKeyFactory()
        old_key_value = api_key.key
        api_key.refresh_key()
        assert api_key.key != old_key_value

    @pytest.mark.django_db
    def test_initial_save_without_pk_creates_key(self):
        api_key = APIKeyFactory(key="")
        api_key.pk = None
        api_key.save()

        assert bool(api_key.key) is True

    def test_get_absolute_delete_url(self):
        key = APIKeyFactory.build(pk=1)
        assert key.get_absolute_delete_url() == reverse(
            "users:delete-key", kwargs={"pk": 1}
        )

    def test_get_absolute_refresh_url(self):
        key = APIKeyFactory.build(pk=1)
        assert key.get_absolute_refresh_url() == reverse(
            "users:refresh-key", kwargs={"pk": 1}
        )
