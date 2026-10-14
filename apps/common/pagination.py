"""Manual ``skip``/``limit`` pagination.

List endpoints return plain JSON arrays with ``skip``/``limit`` query
params (default ``limit=100``). DRF's global paginator is disabled, so each
list view slices the queryset itself.
"""
from rest_framework.exceptions import ValidationError


def get_skip_limit(request, default_limit: int = 100) -> tuple[int, int]:
    params = request.query_params

    raw_skip = params.get("skip", 0)
    raw_limit = params.get("limit", default_limit)

    try:
        skip = int(raw_skip)
    except (TypeError, ValueError):
        raise ValidationError({"skip": ["A valid integer is required."]})

    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        raise ValidationError({"limit": ["A valid integer is required."]})

    return max(skip, 0), max(limit, 0)
