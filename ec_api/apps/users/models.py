import binascii
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from users.managers import CustomUserManager
from users.mixins import TimestampMixin


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom implementation of django User model to use the email for login
    """

    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = CustomUser.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this user.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class APIKey(TimestampMixin, models.Model):

    name = models.CharField(
        max_length=255, help_text="To help identify your key"
    )
    usage_reason = models.TextField(
        help_text="Short description of the usage reason for this key"
    )
    key = models.CharField(max_length=255)
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    def __str__(self):
        return self.name

    @classmethod
    def _generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        """
        On initial save generates a key
        """
        if not self.key:
            self.key = self._generate_key()

        return super().save(*args, **kwargs)

    def refresh_key(self):
        """
        Creates a new key value and saves
        """
        self.key = self._generate_key()
        self.save()

    def get_absolute_delete_url(self):
        """
        Build URL to delete the key
        """
        return reverse("users:delete-key", kwargs={"pk": self.pk})

    def get_absolute_refresh_url(self):
        """
        Build URL to refresh the key
        """
        return reverse("users:refresh-key", kwargs={"pk": self.pk})
