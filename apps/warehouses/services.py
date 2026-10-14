"""Warehouse service layer."""
from __future__ import annotations

from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework.exceptions import NotFound

from apps.products.models import Product, ProductStock
from apps.warehouses.models import Warehouse


def set_stock(product_id: int, warehouse_id: int, quantity: int) -> ProductStock:
    product = Product.objects.filter(pk=product_id).first()
    if not product:
        raise NotFound("Product not found")

    if not Warehouse.objects.filter(pk=warehouse_id).exists():
        raise NotFound("Warehouse not found")

    entry = ProductStock.objects.filter(
        product_id=product_id, warehouse_id=warehouse_id
    ).first()
    if entry:
        entry.quantity = quantity
        entry.save(update_fields=["quantity"])
    else:
        entry = ProductStock.objects.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
        )

    _sync_product_total(product)
    return entry


def _sync_product_total(product: Product) -> None:
    total = ProductStock.objects.filter(product=product).aggregate(
        total=Coalesce(Sum("quantity"), 0)
    )["total"]
    product.stock = total or 0
    product.save(update_fields=["stock"])
