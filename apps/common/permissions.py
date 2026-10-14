"""Permission classes for the authentication contract.

Semantics:

* missing/invalid token      -> 401
* valid token, user inactive -> 403 ("User is inactive")
* valid token, wrong role    -> 403 ("Requires role: admin")
"""
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from apps.users.models import UserRole


class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            # Let DRF decide between 401 (unauthenticated) / 403.
            return False
        if not user.is_active:
            raise PermissionDenied("User is inactive")
        return True


class IsAdmin(IsAuthenticatedAndActive):
    """Requires an authenticated, active user with the admin role."""

    def has_permission(self, request, view) -> bool:
        if not super().has_permission(request, view):
            return False
        if request.user.role != UserRole.ADMIN:
            raise PermissionDenied("Requires role: admin")
        return True
