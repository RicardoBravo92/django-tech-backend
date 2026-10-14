"""Product serializers.

Decimal fields keep DRF's default string coercion (``"20.00"``).
"""
from rest_framework import serializers


class ProductSpecSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    key = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=255)


class ProductSpecWriteSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=255)


class ProductSerializer(serializers.Serializer):
    """Product read model."""

    id = serializers.IntegerField(read_only=True)
    sku = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_null=True, required=False)
    brand_id = serializers.IntegerField(allow_null=True, required=False)
    category_id = serializers.IntegerField(allow_null=True, required=False)
    cost_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    sale_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock = serializers.IntegerField()
    image_url = serializers.CharField(allow_null=True, required=False)
    is_active = serializers.BooleanField()
    specs = ProductSpecSerializer(many=True, read_only=True)


class ProductCreateSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)
    description = serializers.CharField(
        allow_null=True, required=False, default=None
    )
    brand_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    category_id = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    cost_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=0, default=0
    )
    sale_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=0, default=0
    )
    stock = serializers.IntegerField(min_value=0, default=0)
    image_url = serializers.CharField(
        max_length=500, allow_null=True, required=False, default=None
    )
    is_active = serializers.BooleanField(default=True)
    specs = ProductSpecWriteSerializer(many=True, required=False, default=list)


class ProductUpdateSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=64, required=False)
    name = serializers.CharField(max_length=255, required=False)
    slug = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(allow_null=True, required=False)
    brand_id = serializers.IntegerField(required=False, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    cost_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    sale_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    stock = serializers.IntegerField(required=False)
    image_url = serializers.CharField(
        max_length=500, allow_null=True, required=False
    )
    is_active = serializers.BooleanField(required=False)
    specs = ProductSpecWriteSerializer(many=True, required=False)
