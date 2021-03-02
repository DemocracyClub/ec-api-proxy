from .base import *  # noqa
import os

ALLOWED_HOSTS = ["*"]
DEBUG = os.environ.get("DEBUG", False)

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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST"),
        "NAME": os.environ.get("POSTGRES_DATABASE_NAME"),
        "USER": "postgres",
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

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

STATIC_ROOT = os.path.join(BASE_DIR, "static_files")

setup_sentry()
