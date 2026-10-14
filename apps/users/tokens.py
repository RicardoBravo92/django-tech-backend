"""Refresh-token issuance / rotation / revocation.

Row locks are taken with
``select_for_update`` inside a transaction (a no-op on SQLite, real on
PostgreSQL).
"""
from __future__ import annotations

import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.users.models import RefreshToken


def _expiry():
    return timezone.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def issue_refresh_token(user_id: int) -> RefreshToken:
    return RefreshToken.objects.create(
        user_id=user_id,
        token=secrets.token_urlsafe(48),
        expires_at=_expiry(),
    )


def rotate(raw_token: str) -> RefreshToken | None:
    with transaction.atomic():
        stored = (
            RefreshToken.objects.select_for_update()
            .filter(token=raw_token)
            .first()
        )
        if not stored or stored.revoked or stored.expires_at < timezone.now():
            return None
        stored.revoked = True
        stored.save(update_fields=["revoked"])
        return issue_refresh_token(stored.user_id)


def revoke(raw_token: str) -> None:
    stored = RefreshToken.objects.filter(token=raw_token).first()
    if stored and not stored.revoked:
        stored.revoked = True
        stored.save(update_fields=["revoked"])


def revoke_for_user(raw_token: str, user_id: int) -> bool:
    with transaction.atomic():
        stored = (
            RefreshToken.objects.select_for_update()
            .filter(token=raw_token)
            .first()
        )
        if not stored or stored.user_id != user_id:
            return False
        stored.revoked = True
        stored.save(update_fields=["revoked"])
        return True
