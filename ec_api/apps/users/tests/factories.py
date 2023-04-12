import factory
from faker import Faker
from users.models import APIKey, CustomUser

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker("email")

    class Meta:
        model = CustomUser


class APIKeyFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("sentence")
    usage_reason = factory.Faker("paragraph")
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = APIKey
