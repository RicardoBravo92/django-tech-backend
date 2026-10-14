"""Report endpoints -- every route requires an admin.

Query params ``start``/``end`` default to the start of the current month and
"now" (UTC).
"""
from __future__ import annotations

from datetime import datetime, timezone

from django.utils import timezone as dj_timezone
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdmin
from apps.reports import services


def _start_of_month() -> datetime:
    now = dj_timezone.now()
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _now() -> datetime:
    return dj_timezone.now()


def _parse_datetime_param(request, name: str, default) -> datetime:
    raw = request.query_params.get(name)
    if raw in (None, ""):
        return default()
    parsed = parse_datetime(raw)
    if parsed is None:
        raise ValidationError({name: ["Invalid datetime format."]})
    if dj_timezone.is_naive(parsed):
        parsed = dj_timezone.make_aware(parsed, timezone.utc)
    return parsed


def _limit_param(request, default: int = 10) -> int:
    raw = request.query_params.get("limit")
    if raw in (None, ""):
        return default
    try:
        limit = int(raw)
    except (TypeError, ValueError):
        raise ValidationError({"limit": ["A valid integer is required."]})
    if limit < 1 or limit > 50:
        raise ValidationError({"limit": ["Must be between 1 and 50."]})
    return limit


class SalesReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        start = _parse_datetime_param(request, "start", _start_of_month)
        end = _parse_datetime_param(request, "end", _now)
        return Response(services.sales_summary(start, end))


class SalesDailyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        start = _parse_datetime_param(request, "start", _start_of_month)
        end = _parse_datetime_param(request, "end", _now)
        return Response(services.sales_by_day(start, end))


class BestSellersView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        start = _parse_datetime_param(request, "start", _start_of_month)
        end = _parse_datetime_param(request, "end", _now)
        limit = _limit_param(request)
        return Response(services.best_sellers(start, end, limit))


class ProfitReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        start = _parse_datetime_param(request, "start", _start_of_month)
        end = _parse_datetime_param(request, "end", _now)
        return Response(services.profit(start, end))
