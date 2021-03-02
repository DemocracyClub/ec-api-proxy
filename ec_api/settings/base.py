import os
import dc_design_system

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))


def here(*path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *path)


PROJECT_ROOT = here("..")


def root(*path):
    return os.path.join(os.path.abspath(PROJECT_ROOT), *path)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "frontend",
    "pipeline",
    "dc_design_system",
    "users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ec_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ec_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@api.ec-dc.club"


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.CustomUser"

# django-sesame settings
AUTHENTICATION_BACKENDS = ["sesame.backends.ModelBackend"]
SESAME_MAX_AGE = 60 * 10
SESAME_ONE_TIME = True
SESAME_TOKEN_NAME = "login_token"

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-GB"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = (root("assets"),)
STATIC_ROOT = root("static")
STATICFILES_STORAGE = "pipeline.storage.PipelineManifestStorage"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "pipeline.finders.PipelineFinder",
    "pipeline.finders.CachedFileFinder",
)

PIPELINE = {
    "COMPILERS": ("pipeline.compilers.sass.SASSCompiler",),
    "SASS_BINARY": "pysassc",
    "CSS_COMPRESSOR": "pipeline.compressors.NoopCompressor",
    "STYLESHEETS": {
        "styles": {
            "source_filenames": ("scss/styles.scss",),
            "output_filename": "css/styles.css",
            "extra_context": {
                "media": "screen,projection",
            },
        },
    },
}

PIPELINE["SASS_ARGUMENTS"] = (
    " -I " + dc_design_system.DC_SYSTEM_PATH + "/system"
)


def setup_sentry(environment=None):
    if not environment:
        environment = os.environ.get("SAM_LAMBDA_CONFIG_ENV")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    release = os.environ.get("GIT_HASH", "unknown")
    if SENTRY_DSN and environment:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=1.0,
            environment=environment,
            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True,
            release=release,
        )


# Lambda: https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime
# CircleCI: https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables
# Make: https://docs.oracle.com/cd/E19504-01/802-5880/makeattapp-21/index.html
def is_local_dev():
    vars_to_check = ["AWS_LAMBDA_FUNCTION_NAME", "CI", "MAKEFLAGS"]
    return not any(ev in os.environ for ev in vars_to_check)


# .local.py overrides all the common settings.
if is_local_dev():
    try:
        from .local import *  # noqa
    except ImportError:
        pass


def is_running_tests():
    if os.environ.get("RUN_ENV") == "test":
        return True
    if "CI" in os.environ:
        return True
    return False


if is_running_tests():
    try:
        from .testing import *  # noqa
    except ImportError:
        pass
