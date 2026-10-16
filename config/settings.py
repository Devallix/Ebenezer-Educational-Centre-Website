"""
Django settings for the Ebenezer Educational Centre website.

This project uses exactly ONE settings module.  Development and production
behaviour are distinguished with environment variables (see ``.env.example``).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / "apps"

load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-development-only-key-change-me-before-deploying",
)

DEBUG = env_bool("DEBUG", default=True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:8000").rstrip("/")

if not DEBUG:
    if SECRET_KEY.startswith("django-insecure-"):
        raise ValueError(
            "SECRET_KEY must be set to a secure value when DEBUG=False."
        )
    if not ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be configured when DEBUG=False.")

# Set by the deployment environment to refuse a silently unsuitable database.
REQUIRE_PRODUCTION_DB = env_bool("REQUIRE_PRODUCTION_DB", default=False)

INSTALLED_APPS = [
    # Local apps
    "apps.core",
    "apps.accounts",
    "apps.school",
    "apps.academics",
    "apps.admissions",
    "apps.gallery",
    "apps.dashboard",
    "apps.analytics",
    "apps.seo",
    # Third party
    "crispy_forms",
    "crispy_bootstrap5",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
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
    "apps.analytics.middleware.AnalyticsMiddleware",
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
                "apps.core.context_processors.site_context",
                "apps.core.context_processors.dashboard_context",
                "apps.seo.context_processors.seo_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.environ.get("DATABASE_CONN_MAX_AGE", "600")),
            ssl_require=env_bool("DATABASE_SSL_REQUIRE", default=False),
        )
    }
elif REQUIRE_PRODUCTION_DB:
    raise ValueError(
        "DATABASE_URL is required for this deployment but is not set. "
        "Configure a PostgreSQL (or compatible) DATABASE_URL."
    )
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {"timeout": 20},
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:overview"
LOGOUT_REDIRECT_URL = "core:home"

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-gb"
TIME_ZONE = os.environ.get("TIME_ZONE", "Africa/Accra")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "Ebenezer Educational Centre <noreply@localhost>"
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "15"))

SCHOOL_NOTIFICATION_EMAIL = os.environ.get("SCHOOL_NOTIFICATION_EMAIL", "")

# ---------------------------------------------------------------------------
# Crispy Forms
# ---------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ---------------------------------------------------------------------------
# Sessions & security
# ---------------------------------------------------------------------------
SESSION_COOKIE_AGE = int(os.environ.get("SESSION_COOKIE_AGE", "1209600"))
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO" if not DEBUG else "WARNING")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "apps": {"level": LOG_LEVEL, "handlers": ["console"], "propagate": False},
        "django.security": {
            "level": LOG_LEVEL,
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {"level": LOG_LEVEL, "handlers": ["console"]},
}

# ---------------------------------------------------------------------------
# Project-specific configuration
# ---------------------------------------------------------------------------
# Login throttling (simple in-process counter, per username + IP).
LOGIN_RATE_LIMIT = int(os.environ.get("LOGIN_RATE_LIMIT", "10"))
LOGIN_RATE_WINDOW = int(os.environ.get("LOGIN_RATE_WINDOW", "300"))

# Analytics retention in days; 0 disables automatic purging.
ANALYTICS_RETENTION_DAYS = int(os.environ.get("ANALYTICS_RETENTION_DAYS", "180"))

# Maximum upload sizes (bytes).
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", str(5 * 1024 * 1024)))

ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico", ".svg"]

# Roles
ROLE_SUPER_ADMIN = "superadmin"
ROLE_WEBSITE_ADMIN = "webadmin"
ROLE_ADMISSIONS_OFFICER = "admissions"
ROLE_CONTENT_EDITOR = "editor"
ROLE_CHOICES = [
    (ROLE_SUPER_ADMIN, "Super Administrator"),
    (ROLE_WEBSITE_ADMIN, "Website Administrator"),
    (ROLE_ADMISSIONS_OFFICER, "Admissions Officer"),
    (ROLE_CONTENT_EDITOR, "Content Editor"),
]

if "test" in sys.argv or "pytest" in sys.argv:
    # Keep password hashing fast while running the test suite.
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
