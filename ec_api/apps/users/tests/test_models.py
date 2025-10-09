from unittest.mock import patch

import pytest
from django.urls import reverse
from users.tests.factories import APIKeyFactory


class TestAPIKeyModel:
    @pytest.mark.django_db
    def test_refresh_key(self):
        api_key = APIKeyFactory()
        old_key_value = api_key.key
        with patch(
            "users.logging_helpers.APIKeyForLogging.upload_to_s3"
        ) as mock_upload_to_s3:
            api_key.refresh_key()
            mock_upload_to_s3.assert_called_once()
        assert api_key.key != old_key_value

    @pytest.mark.django_db
    def test_initial_save_without_pk_creates_key(self):
        api_key = APIKeyFactory(key="")
        api_key.pk = None
        with patch(
            "users.logging_helpers.APIKeyForLogging.upload_to_s3"
        ) as mock_upload_to_s3:
            api_key.save()
            mock_upload_to_s3.assert_called_once()

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
