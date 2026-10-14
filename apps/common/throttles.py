"""Rate limiting.

Throttling configuration:

* a per-endpoint scoped limit (``throttle_scope`` on the view), and
* a blanket ``60/minute`` default for every endpoint.

``ScopedRateThrottle`` reads the rate lazily inside ``allow_request``, so it is
safe to subclass and short-circuit when throttling is disabled.
"""
from django.conf import settings
from rest_framework.throttling import ScopedRateThrottle


class ConditionalScopedRateThrottle(ScopedRateThrottle):
    def allow_request(self, request, view) -> bool:
        if not getattr(settings, "RATE_LIMIT_ENABLED", True):
            return True
        return super().allow_request(request, view)
