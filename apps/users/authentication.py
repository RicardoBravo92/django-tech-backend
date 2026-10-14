"""DRF authentication for the JWT access tokens.

Public endpoints tolerate garbage/absent tokens, so
``authenticate`` returns ``None`` (rather than raising) whenever the header is
missing or the token is invalid/expired.  A *valid* token always yields the
matching user -- including inactive users -- so that permission classes can
raise the correct 403 ("User is inactive").
"""
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from apps.users.jwt import decode_token
from apps.users.models import User


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header or header[0].lower() != self.keyword.lower().encode():
            return None
        if len(header) != 2:
            return None

        try:
            token = header[1].decode()
        except UnicodeError:
            return None

        subject = decode_token(token)
        if not subject:
            return None

        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            return None

        user = User.objects.filter(pk=user_id).first()
        if user is None:
            return None

        return (user, token)

    def authenticate_header(self, request) -> str:
        # Ensures DRF responds 401 (not 403) when no credentials are supplied.
        return 'Bearer realm="api"'
