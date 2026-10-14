"""User-facing transactional email (Resend) + password-reset flow."""
from __future__ import annotations

import html
import uuid
from datetime import timedelta

import resend
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.exceptions import BadRequest, EmailSendFailed
from apps.users.models import PasswordResetToken, User

resend.api_key = settings.RESEND_API_KEY


def _send(to: str, subject: str, html_body: str) -> None:
    try:
        resend.Emails.send(
            {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html_body,
            }
        )
    except resend.exceptions.ResendError:
        raise EmailSendFailed()


def send_registration_email(user: User) -> None:
    name = html.escape(user.full_name)
    _send(
        to=user.email,
        subject="Welcome to Tech!",
        html_body=f"""
        <h2>Welcome to Tech, {name}!</h2>
        <p>Your account has been created successfully.</p>
        <p>You can now log in and start shopping.</p>
        <p>If you did not create this account, please ignore this email.</p>
        """,
    )


def request_password_reset(user: User) -> str:
    token = uuid.uuid4().hex
    now = timezone.now()

    # Invalidate any outstanding tokens for this user.
    PasswordResetToken.objects.filter(
        user=user,
        used=False,
        expires_at__gt=now,
    ).update(used=True)

    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=now
        + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES),
    )

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    name = html.escape(user.full_name)
    _send(
        to=user.email,
        subject="Password Reset Request",
        html_body=f"""
        <h2>Password Reset</h2>
        <p>Hi {name},</p>
        <p>You requested a password reset. Click the link below to set a new
        password. The link expires in
        {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>If you did not request this, please ignore this email.</p>
        """,
    )
    return token


def reset_password(token: str, new_password: str) -> None:
    with transaction.atomic():
        record = (
            PasswordResetToken.objects.select_for_update()
            .filter(token=token, used=False)
            .first()
        )
        if not record or record.expires_at < timezone.now():
            raise BadRequest("Invalid or expired password reset token")

        user = User.objects.filter(pk=record.user_id).first()
        if not user:
            raise BadRequest("Invalid or expired password reset token")

        record.used = True
        record.save(update_fields=["used"])

        user.set_password(new_password)
        user.save(update_fields=["password"])
