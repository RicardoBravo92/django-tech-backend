"""Authentication + user endpoints."""
from __future__ import annotations

from rest_framework.exceptions import AuthenticationFailed, NotFound, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import Conflict, EmailSendFailed
from apps.common.pagination import get_skip_limit
from apps.common.permissions import IsAdmin, IsAuthenticatedAndActive
from apps.users import emails, services, tokens
from apps.users.jwt import create_access_token
from apps.users.models import User, UserRole
from apps.users.serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RefreshSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
)


def _token_payload(user_id: int, refresh_token: str) -> dict:
    return {
        "access_token": create_access_token(str(user_id)),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = services.authenticate(
            serializer.validated_data["email"],
            serializer.validated_data["password"],
        )
        if not user:
            raise AuthenticationFailed("Incorrect email or password")
        if not user.is_active:
            raise PermissionDenied("User is inactive")

        refresh = tokens.issue_refresh_token(user.id)
        return Response(_token_payload(user.id, refresh.token))


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "register"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        if services.email_exists(email):
            raise Conflict("Email already registered")

        user = services.create_user(
            email=email,
            full_name=serializer.validated_data["full_name"],
            password=serializer.validated_data["password"],
            role=UserRole.CUSTOMER,
        )

        try:
            emails.send_registration_email(user)
        except EmailSendFailed:
            # Registration must succeed even if the welcome email fails
            # (errors from the send are swallowed here).
            pass

        return Response(UserSerializer(user).data, status=201)


class RefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "refresh"

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_token = tokens.rotate(serializer.validated_data["refresh_token"])
        if not new_token:
            raise AuthenticationFailed("Invalid or expired refresh token")

        return Response(_token_payload(new_token.user_id, new_token.token))


class LogoutView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not tokens.revoke_for_user(
            serializer.validated_data["refresh_token"], request.user.id
        ):
            raise AuthenticationFailed("Invalid or expired refresh token")

        return Response(status=204)


class MeView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "forgot_password"

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email=serializer.validated_data["email"], is_active=True
        ).first()
        if user:
            emails.request_password_reset(user)

        return Response(status=204)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "reset_password"

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emails.reset_password(
            serializer.validated_data["token"],
            serializer.validated_data["new_password"],
        )
        return Response(status=204)


class UserListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAuthenticatedAndActive()]

    def get(self, request):
        skip, limit = get_skip_limit(request)
        users = services.list_users(skip=skip, limit=limit)
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        if services.email_exists(email):
            raise Conflict("Email already registered")

        user = services.create_user(
            email=email,
            full_name=serializer.validated_data["full_name"],
            password=serializer.validated_data["password"],
            role=serializer.validated_data.get("role", UserRole.SALES),
        )
        return Response(UserSerializer(user).data, status=201)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, user_id: int):
        user = services.get_user(user_id)
        if not user:
            raise NotFound("User not found")
        return Response(UserSerializer(user).data)
