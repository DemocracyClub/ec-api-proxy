from users.forms import RegisterForm
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRegisterForm:
    def test_save(self, mocker):
        save = mocker.MagicMock()
        user = mocker.MagicMock(spec=User)
        mocker.patch("django.forms.models.ModelForm.save", new=save)

        form = RegisterForm(instance=user)
        form.save()

        user.set_unusable_password.assert_called_once()
        save.assert_called_once_with(commit=True)
