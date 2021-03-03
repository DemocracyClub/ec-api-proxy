from users.forms import LoginForm
from django.contrib.auth import get_user_model

User = get_user_model()


class TestLoginForm:
    def test_clean_email(self):
        form = LoginForm()
        form.cleaned_data = {"email": "michael@EMAIL.COM"}
        form.clean_email()
        assert form.clean_email() == "michael@email.com"
