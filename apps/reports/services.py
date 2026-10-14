"""Aggregation queries for the report endpoints.

Plain ``dict`` results are returned; DRF's JSON encoder converts ``Decimal``
values to ``float``.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce, TruncDate

from apps.orders.models import Order, OrderItem, OrderStatus

_PAID = OrderStatus.PAID
_MONEY = DecimalField(max_digits=16, decimal_places=2)
_CENT = Decimal("0.01")


def _dec(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value if value is not None else 0))


def _paid_orders(start: datetime, end: datetime):
    return Order.objects.filter(
        status=_PAID, created_at__gte=start, created_at__lte=end
    )


def sales_summary(start: datetime, end: datetime) -> dict:
    agg = _paid_orders(start, end).aggregate(
        orders=Count("id"),
        revenue=Coalesce(Sum("total"), Decimal("0")),
        tax=Coalesce(Sum("tax_amount"), Decimal("0")),
        discounts=Coalesce(Sum("discount_amount"), Decimal("0")),
    )
    return {
        "orders": agg["orders"],
        "revenue": _dec(agg["revenue"]),
        "tax_collected": _dec(agg["tax"]),
        "discounts_given": _dec(agg["discounts"]),
    }


def sales_by_day(start: datetime, end: datetime) -> list[dict]:
    rows = (
        _paid_orders(start, end)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            orders=Count("id"),
            revenue=Coalesce(Sum("total"), Decimal("0")),
        )
        .order_by("day")
    )
    return [
        {
            "day": row["day"].isoformat(),
            "orders": row["orders"],
            "revenue": _dec(row["revenue"]),
        }
        for row in rows
    ]


def best_sellers(
    start: datetime, end: datetime, limit: int = 10
) -> list[dict]:
    rows = (
        OrderItem.objects.filter(
            order__status=_PAID,
            order__created_at__gte=start,
            order__created_at__lte=end,
        )
        .values("product_id", "product__name")
        .annotate(
            units=Sum("quantity"),
            gross=Sum(F("unit_price") * F("quantity"), output_field=_MONEY),
        )
        .order_by("-units")[:limit]
    )
    return [
        {
            "product": row["product__name"],
            "units": row["units"],
            "gross": _dec(row["gross"]),
        }
        for row in rows
    ]


def profit(start: datetime, end: datetime) -> dict:
    gross = OrderItem.objects.filter(
        order__status=_PAID,
        order__created_at__gte=start,
        order__created_at__lte=end,
    ).aggregate(
        gp=Coalesce(
            Sum(
                F("unit_price") * F("quantity")
                - F("product__cost_price") * F("quantity"),
                output_field=_MONEY,
            ),
            Decimal("0"),
        )
    )["gp"]

    summary = sales_summary(start, end)
    revenue = summary["revenue"]
    gross_profit = _dec(gross)

    return {
        "revenue": revenue,
        "gross_profit": gross_profit,
        "profit_margin_pct": (
            (gross_profit / revenue * 100).quantize(_CENT)
            if revenue
            else Decimal("0")
        ),
    }
