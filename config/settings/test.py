"""Test settings.

Uses an in-memory SQLite database and fully disables rate limiting so the
test suite runs deterministically without external services.
"""
from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Belt-and-braces: no throttling during tests.
RATE_LIMIT_ENABLED = False
REST_FRAMEWORK = {**REST_FRAMEWORK}  # copy so we don't mutate base
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []

# Keep password hashing fast in tests while staying on argon2.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

SECRET_KEY = "test-secret-key-that-is-definitely-long-enough-32chars"
