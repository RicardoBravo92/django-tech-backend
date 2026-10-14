"""Password strength validation.

Rules:

* at least 8 characters
* at most 128 characters
* must contain both letters and numbers
"""
from rest_framework.exceptions import ValidationError


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    if len(password) > 128:
        raise ValidationError("Password must be at most 128 characters long")
    if password.isdigit() or password.isalpha():
        raise ValidationError("Password must contain both letters and numbers")
    return password
