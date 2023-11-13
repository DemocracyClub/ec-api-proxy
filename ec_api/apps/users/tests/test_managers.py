import pytest
from faker import Faker
from users.models import CustomUser

fake = Faker()


@pytest.mark.django_db
class TestCustomUserManager:
    def test_create_user(self):
        user = CustomUser.objects.create_user(email="example@email.com")
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.email == "example@email.com"
        assert bool(user.pk) is True

    def test_create_superuser(self):
        superuser = CustomUser.objects.create_superuser(
            email="example@email.com",
            password=fake.password(),
        )
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert bool(superuser.pk) is True

    def test__create_user_no_email(self):
        with pytest.raises(ValueError):
            CustomUser.objects._create_user(
                email=None, password=fake.password()
            )

    def test__create_user_with_email(self):
        user = CustomUser.objects._create_user(
            email="example@EMAIL.COM", password=fake.password()
        )
        assert user.email == "example@email.com"
        assert bool(user.pk) is True
