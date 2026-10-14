from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """``GET /health`` -> ``{"status": "ok"}`` (10 requests/minute).

    ``throttle_scope`` is picked up by the globally configured
    ``ConditionalScopedRateThrottle``.
    """

    permission_classes = [AllowAny]
    throttle_scope = "health"

    def get(self, request):
        return Response({"status": "ok"})
