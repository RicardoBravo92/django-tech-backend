"""Warehouse serializers.

``WarehouseSerializer`` (id, name, location, no timestamps).
``StockSerializer`` (product_id, warehouse_id, quantity).
"""
from rest_framework import serializers


class WarehouseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    location = serializers.CharField(allow_null=True, required=False)


class WarehouseCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    location = serializers.CharField(
        max_length=255, allow_null=True, required=False, default=None
    )


class WarehouseUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(
        max_length=255, allow_null=True, required=False
    )


class StockSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(read_only=True)
    warehouse_id = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
