from rest_framework import serializers

from apps.users.models import User, UserRole
from apps.users.validators import validate_password_strength


class UserSerializer(serializers.ModelSerializer):
    """User read model."""

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "is_active", "created_at"]
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """Public self-registration; the role is always forced to ``customer``."""

    email = serializers.EmailField(max_length=255)
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate_password(self, value: str) -> str:
        return validate_password_strength(value)


class UserCreateSerializer(serializers.Serializer):
    """Admin-created user."""

    email = serializers.EmailField(max_length=255)
    full_name = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(
        choices=UserRole.choices, default=UserRole.SALES
    )
    password = serializers.CharField(max_length=128, write_only=True)

    def validate_password(self, value: str) -> str:
        return validate_password_strength(value)


class LoginSerializer(serializers.Serializer):
    # Plain strings here (no email-format validation).
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128)


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    new_password = serializers.CharField(max_length=128, write_only=True)

    def validate_new_password(self, value: str) -> str:
        return validate_password_strength(value)
