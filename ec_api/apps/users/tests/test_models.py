from django.urls import reverse

from users.tests.factories import APIKeyFactory


class TestAPIKeyModel:
    def test_get_absolute_delete_url(self):
        key = APIKeyFactory.build(pk=1)
        assert key.get_absolute_delete_url() == reverse(
            "users:delete-key", kwargs={"pk": 1}
        )
