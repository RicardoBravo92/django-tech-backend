"""Custom API exceptions.

Every error is rendered as a ``{"detail": "..."}`` body; DRF's
``APIException`` subclasses produce that shape.
"""
from rest_framework.exceptions import APIException


class Conflict(APIException):
    """409 conflicts: duplicate email, insufficient stock, double payment."""

    status_code = 409
    default_detail = "Conflict"
    default_code = "conflict"


class BadRequest(APIException):
    """400 for logically invalid input (e.g. invalid reset token)."""

    status_code = 400
    default_detail = "Bad request"
    default_code = "bad_request"


class EmailSendFailed(APIException):
    """502 returned when the Resend API rejects an outgoing email."""

    status_code = 502
    default_detail = "Failed to send email"
    default_code = "email_send_failed"
