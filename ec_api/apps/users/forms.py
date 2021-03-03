from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

__all__ = ["LoginForm"]


class LoginForm(forms.Form):
    """
    Login form for a User.
    """

    email = forms.EmailField(required=True)

    def clean_email(self):
        """
        Normalize the entered email
        """
        email = self.cleaned_data["email"]
        return User.objects.normalize_email(email)
