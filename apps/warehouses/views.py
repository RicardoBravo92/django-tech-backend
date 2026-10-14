"""Warehouse endpoints (admin only)."""
from __future__ import annotations

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdmin
from apps.products.models import ProductStock
from apps.warehouses import services
from apps.warehouses.models import Warehouse
from apps.warehouses.serializers import (
    StockSerializer,
    WarehouseCreateSerializer,
    WarehouseSerializer,
    WarehouseUpdateSerializer,
)


def _required_int_query_param(request, name: str) -> int:
    raw = request.query_params.get(name)
    if raw in (None, ""):
        raise ValidationError({name: ["This query parameter is required."]})
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValidationError({name: ["A valid integer is required."]})


class WarehouseListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        warehouses = Warehouse.objects.order_by("id")
        return Response(WarehouseSerializer(warehouses, many=True).data)

    def post(self, request):
        serializer = WarehouseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warehouse = Warehouse.objects.create(**serializer.validated_data)
        return Response(WarehouseSerializer(warehouse).data, status=201)


class WarehouseDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get_object(self, warehouse_id: int) -> Warehouse:
        warehouse = Warehouse.objects.filter(pk=warehouse_id).first()
        if not warehouse:
            raise NotFound("Warehouse not found")
        return warehouse

    def patch(self, request, warehouse_id: int):
        warehouse = self._get_object(warehouse_id)
        serializer = WarehouseUpdateSerializer(
            warehouse, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(warehouse, field, value)
        warehouse.save()
        return Response(WarehouseSerializer(warehouse).data)

    def delete(self, request, warehouse_id: int):
        self._get_object(warehouse_id).delete()
        return Response(status=204)


class ProductStockView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, product_id: int):
        entries = ProductStock.objects.filter(product_id=product_id).order_by("id")
        return Response(StockSerializer(entries, many=True).data)

    def put(self, request, product_id: int):
        warehouse_id = _required_int_query_param(request, "warehouse_id")
        quantity = _required_int_query_param(request, "quantity")

        entry = services.set_stock(product_id, warehouse_id, quantity)
        return Response(StockSerializer(entry).data)
