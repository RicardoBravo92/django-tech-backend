"""Production settings.

Expects SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS and CORS_ORIGINS to be
provided through the environment.
"""
from .base import *  # noqa: F401,F403
from .base import env_bool, env_list

DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", [])

# Security hardening (behind a TLS-terminating proxy).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
