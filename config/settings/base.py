"""Base settings shared by every environment.

Configuration is read from environment variables (optionally loaded from a
``.env`` file at the project root).
"""
from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths & environment loading
# ---------------------------------------------------------------------------
# backendDjango/  (manage.py lives here)
BASE_DIR = Path(__file__).resolve().parents[2]

# Load .env without overriding already-exported variables.
load_dotenv(BASE_DIR / ".env")


def env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------
# An empty / default / short secret key is rejected. A long development
# fallback keeps a fresh clone booting with zero configuration while still
# refusing genuinely weak values.
_DEV_SECRET_KEY = "dev-secret-key-change-me-to-a-long-random-string-32b-min"
_WEAK_SECRET_KEYS = {"", "change-me-in-production", "change-me-in-production "}

SECRET_KEY = env("SECRET_KEY", _DEV_SECRET_KEY) or ""
if SECRET_KEY in _WEAK_SECRET_KEYS or len(SECRET_KEY) < 32:
    raise ImproperlyConfigured(
        "SECRET_KEY must be at least 32 characters long and must not be the "
        "default value. Set it in your environment or .env file."
    )

# Signing algorithm; ``ALGORITHM`` is accepted as an alias.
JWT_ALGORITHM = env("JWT_ALGORITHM") or env("ALGORITHM", "HS256")
if JWT_ALGORITHM not in {"HS256", "HS384", "HS512"}:
    raise ImproperlyConfigured(
        "JWT_ALGORITHM must be one of HS256, HS384, HS512."
    )

DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "testserver"])

# ---------------------------------------------------------------------------
# Token / business configuration
# ---------------------------------------------------------------------------
ACCESS_TOKEN_EXPIRE_MINUTES = env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
REFRESH_TOKEN_EXPIRE_DAYS = env_int("REFRESH_TOKEN_EXPIRE_DAYS", 7)
PASSWORD_RESET_EXPIRE_MINUTES = env_int("PASSWORD_RESET_EXPIRE_MINUTES", 15)
TAX_RATE = Decimal(str(env("TAX_RATE", "0.18")))
RATE_LIMIT_ENABLED = env_bool("RATE_LIMIT_ENABLED", True)

# ---------------------------------------------------------------------------
# Email (Resend)
# ---------------------------------------------------------------------------
RESEND_API_KEY = env("RESEND_API_KEY", "") or ""
RESEND_FROM_EMAIL = env("RESEND_FROM_EMAIL", "Tech <onboarding@resend.dev>")
FRONTEND_URL = env("FRONTEND_URL", "http://localhost:3000")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
_DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://tech:tech_password@localhost:5433/tech_django"
)


def parse_database_url(url: str) -> dict:
    """Parse a database URL into a Django ``DATABASES`` entry."""
    parsed = urlparse(url)
    scheme = parsed.scheme.split("+")[0].lower()

    if scheme in {"postgres", "postgresql"}:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed.path.lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "",
            "PORT": str(parsed.port or ""),
            "CONN_MAX_AGE": 60,
        }

    if scheme == "sqlite":
        path = parsed.path or ""
        name = path
        if name in {"", "/"}:
            name = ":memory:"
        elif name.startswith("/:memory:"):
            name = ":memory:"
        elif name.startswith("/"):
            name = name.lstrip("/")
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": name}

    raise ImproperlyConfigured(f"Unsupported database scheme: {parsed.scheme!r}")


DATABASES = {
    "default": parse_database_url(env("DATABASE_URL", _DEFAULT_DATABASE_URL)),
}

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "apps.common",
    "apps.users",
    "apps.catalog",
    "apps.products",
    "apps.warehouses",
    "apps.orders",
    "apps.reports",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS: list[dict] = []

# Argon2 first.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# ---------------------------------------------------------------------------
# Internationalisation / static
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env_list("CORS_ORIGINS", ["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # List endpoints return plain JSON arrays with skip/limit pagination, so the
    # global paginator is disabled and views slice manually.
    "DEFAULT_PAGINATION_CLASS": None,
    "PAGE_SIZE": None,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "apps.common.throttles.ConditionalScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        # Default 60/minute for every endpoint.
        "anon": "60/minute",
        "user": "60/minute",
        "default": "60/minute",
        # Endpoint-specific limits.
        "login": "5/minute",
        "register": "5/minute",
        "refresh": "5/minute",
        "forgot_password": "3/minute",
        "reset_password": "5/minute",
        "health": "10/minute",
    },
}
