from .base import *  # noqa
import os

ALLOWED_HOSTS = [os.environ.get("APP_DOMAIN")]
DEBUG = os.environ.get("DEBUG", False)

WHITENOISE_AUTOREFRESH = False
WHITENOISE_STATIC_PREFIX = "/static/"

if os.environ.get("APP_IS_BEHIND_CLOUDFRONT", False) in [
    True,
    "true",
    "True",
    "TRUE",
]:
    USE_X_FORWARDED_HOST = True
else:
    USE_X_FORWARDED_HOST = False
    FORCE_SCRIPT_NAME = "/Prod"
    STATIC_URL = FORCE_SCRIPT_NAME + WHITENOISE_STATIC_PREFIX

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST"),
        "NAME": os.environ.get("POSTGRES_DATABASE_NAME"),
        "USER": "postgres",
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

DC_API_TOKEN = os.environ.get("DC_API_TOKEN")

EMAIL_BACKEND = "django_ses.SESBackend"
AWS_SES_REGION_NAME = "eu-west-2"
AWS_SES_REGION_ENDPOINT = "email.eu-west-2.amazonaws.com"

AWS_S3_SECURE_URLS = False
AWS_S3_USE_SSL = True
AWS_S3_REGION_NAME = "eu-west-2"
AWS_QUERYSTRING_AUTH = False

AWS_STORAGE_BUCKET_NAME = os.environ.get(
    "AWS_STORAGE_BUCKET_NAME", "ec-api-static-assets-development-32sdf4sg4"
)
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3-website.{AWS_S3_REGION_NAME}.amazonaws.com"
)

STATIC_ROOT = os.path.join(BASE_DIR, "static_files")  # noqa: F405

setup_sentry()  # noqa: F405
