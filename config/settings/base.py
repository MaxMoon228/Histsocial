import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="unsafe-dev-key")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = [host.strip() for host in env("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",") if host.strip()]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in env("CSRF_TRUSTED_ORIGINS", default="http://localhost,http://127.0.0.1").split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.common",
    "apps.core",
    "apps.catalog",
    "apps.tests_catalog",
    "apps.events",
    "apps.axis",
    "apps.favorites",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.favorites.context_processors.favorites_context",
                "apps.core.context_processors.site_meta",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

default_db_url = (
    f"postgres://{env('DB_USER', default='chronograph')}:"
    f"{env('DB_PASSWORD', default='chronograph')}@"
    f"{env('DB_HOST', default='db')}:"
    f"{env('DB_PORT', default='5432')}/"
    f"{env('DB_NAME', default='chronograph')}"
)
settings_module = os.getenv("DJANGO_SETTINGS_MODULE", "")
if settings_module.endswith(".dev") and not env("DATABASE_URL", default=""):
    default_db_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

DATABASES = {"default": env.db("DATABASE_URL", default=default_db_url)}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = env("TZ", default="Europe/Moscow")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/staff/login/"
LOGIN_REDIRECT_URL = "/staff/"

FAVORITES_SESSION_KEY = "chronograph_favorites"

HISTORY_CALENDAR_BASE_URL = env(
    "HISTORY_CALENDAR_BASE_URL",
    default="https://historyrussia.org/sobytiya/den-v-istorii.html",
)
HISTORY_CALENDAR_TIMEOUT = env.int("HISTORY_CALENDAR_TIMEOUT", default=20)
HISTORY_CALENDAR_RETRIES = env.int("HISTORY_CALENDAR_RETRIES", default=3)
HISTORY_CALENDAR_SLEEP = env.float("HISTORY_CALENDAR_SLEEP", default=0.5)
HISTORY_CALENDAR_DEFAULT_PAGES = env.int("HISTORY_CALENDAR_DEFAULT_PAGES", default=3)
HISTORY_CALENDAR_WITH_DETAILS = env.bool("HISTORY_CALENDAR_WITH_DETAILS", default=True)
HISTORY_CALENDAR_CRON = env("HISTORY_CALENDAR_CRON", default="0 3 * * *")
HISTORY_CALENDAR_FROM_PAGE = env.int("HISTORY_CALENDAR_FROM_PAGE", default=1)
