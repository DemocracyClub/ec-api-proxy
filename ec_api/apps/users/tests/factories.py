import factory
from faker import Faker
from users.models import CustomUser

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):

    email = factory.Faker("email")

    class Meta:
        model = CustomUser
