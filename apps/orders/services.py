"""Order + Payment service layer."""
from __future__ import annotations

import secrets
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import NotFound

from apps.common.exceptions import Conflict
from apps.orders.models import (
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
)
from apps.products.models import Product

_CENT = Decimal("0.01")


def _tax_rate() -> Decimal:
    return Decimal(str(settings.TAX_RATE))


def get_order(order_id: int) -> Order | None:
    return Order.objects.filter(pk=order_id).first()


def list_user_orders(user_id: int, skip: int = 0, limit: int = 100) -> list[Order]:
    return list(
        Order.objects.filter(user_id=user_id)
        .order_by("-created_at", "-id")
        .prefetch_related("items")[skip : skip + limit]
    )


def create_order(user_id: int, data: dict) -> Order:
    items_in = data["items"]
    product_ids = [item["product_id"] for item in items_in]

    with transaction.atomic():
        products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(
                id__in=product_ids
            )
        }

        for item in items_in:
            product = products.get(item["product_id"])
            if not product:
                raise NotFound(f"Product {item['product_id']} not found")
            if product.stock < item["quantity"]:
                raise Conflict(
                    f"Insufficient stock for {product.name} "
                    f"(available: {product.stock})"
                )
            if not product.is_active:
                raise Conflict(f"Product {product.name} is inactive")

        order = Order.objects.create(
            user_id=user_id,
            shipping_address=data.get("shipping_address"),
            status=OrderStatus.PENDING,
        )

        order_items: list[OrderItem] = []
        for item in items_in:
            product = products[item["product_id"]]
            product.stock -= item["quantity"]
            order_items.append(
                OrderItem(
                    order=order,
                    product_id=product.id,
                    quantity=item["quantity"],
                    unit_price=product.sale_price,
                )
            )

        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(list(products.values()), ["stock"])

        subtotal = sum(
            (item.unit_price * item.quantity for item in order_items), Decimal("0")
        )
        discount = (subtotal * data["discount_percent"] / 100).quantize(_CENT)
        taxable = subtotal - discount
        tax = (taxable * _tax_rate()).quantize(_CENT)
        total = (taxable + tax).quantize(_CENT)

        order.subtotal = subtotal
        order.discount_amount = discount
        order.tax_amount = tax
        order.total = total
        order.save(
            update_fields=[
                "subtotal",
                "discount_amount",
                "tax_amount",
                "total",
                "status",
            ]
        )

    return order


def get_order_payments(order_id: int) -> list[Payment]:
    return list(Payment.objects.filter(order_id=order_id).order_by("id"))


def pay_order(order: Order, data: dict) -> Payment:
    if order.status == OrderStatus.PAID:
        raise Conflict("Order already paid")
    if order.status == OrderStatus.CANCELLED:
        raise Conflict("Order is cancelled")

    with transaction.atomic():
        payment = Payment.objects.create(
            order=order,
            amount=order.total,
            method=data["method"],
            reference=data["reference"] or f"mock-{secrets.token_hex(8)}",
            status=PaymentStatus.SUCCEEDED,
        )
        order.status = OrderStatus.PAID
        order.save(update_fields=["status"])

    return payment
