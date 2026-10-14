"""JWT access-token helpers.

Token payload:

    {"sub": "<user_id>", "exp": <expiry>}

so tokens issued by either service are mutually verifiable (same HS256 secret).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings


def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expires}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError:
        return None
    return payload.get("sub")
