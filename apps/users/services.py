"""User service layer."""
from __future__ import annotations

from apps.users.models import User, UserRole


def create_user(
    email: str,
    full_name: str,
    password: str,
    role: str = UserRole.SALES,
) -> User:
    return User.objects.create_user(
        email=email,
        full_name=full_name,
        password=password,
        role=role,
    )


def get_user(user_id: int) -> User | None:
    return User.objects.filter(pk=user_id).first()


def list_users(skip: int = 0, limit: int = 100) -> list[User]:
    return list(User.objects.order_by("id")[skip : skip + limit])


def email_exists(email: str) -> bool:
    return User.objects.filter(email=email).exists()


def authenticate(email: str, password: str) -> User | None:
    user = User.objects.filter(email=email).first()
    if not user or not user.check_password(password):
        return None
    return user
