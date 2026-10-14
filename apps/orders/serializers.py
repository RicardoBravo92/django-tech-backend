"""Order + Payment serializers."""
from rest_framework import serializers

from apps.orders.models import PaymentMethod


class OrderItemSerializer(serializers.Serializer):
    """Order item read model."""

    id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )


class OrderSerializer(serializers.Serializer):
    """Order read model."""

    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    discount_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    tax_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    shipping_address = serializers.CharField(
        allow_null=True, required=False, read_only=True
    )
    created_at = serializers.DateTimeField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True, allow_empty=False)
    shipping_address = serializers.CharField(
        max_length=500, allow_null=True, required=False, default=None
    )
    discount_percent = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=0,
        max_value=100,
        default=0,
    )


class PaymentSerializer(serializers.Serializer):
    """Payment read model."""

    id = serializers.IntegerField(read_only=True)
    order_id = serializers.IntegerField(read_only=True)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    method = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    reference = serializers.CharField(allow_null=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class PaymentCreateSerializer(serializers.Serializer):
    method = serializers.ChoiceField(
        choices=PaymentMethod.choices, default=PaymentMethod.CARD
    )
    reference = serializers.CharField(
        max_length=255, allow_null=True, required=False, default=None
    )
