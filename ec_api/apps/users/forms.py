from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

__all__ = ["RegisterForm", "LoginForm"]


class RegisterForm(forms.ModelForm):
    """
    Registration form for a User
    """

    class Meta:
        model = User
        fields = ["email"]
        error_messages = {
            "email": {
                "unique": "User with this email has already registered. Do you need to log in?"
            }
        }

    def save(self, commit=True):
        """
        Password field is not used so we set an unusable password before saving
        the instance
        """
        self.instance.set_unusable_password()
        return super().save(commit=commit)


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
