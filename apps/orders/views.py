"""Order + Payment endpoints.

The ``/orders`` and ``/payments`` routers.  ``/orders/me`` is
declared before ``/orders/<id>`` so the literal path always wins.
"""
from __future__ import annotations

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import get_skip_limit
from apps.common.permissions import IsAuthenticatedAndActive
from apps.orders import services
from apps.orders.models import Order
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
)
from apps.users.models import UserRole


def _get_owned_order(request, order_id: int) -> Order:
    order = services.get_order(order_id)
    if not order:
        raise NotFound("Order not found")
    if request.user.role != UserRole.ADMIN and order.user_id != request.user.id:
        raise PermissionDenied("Not your order")
    return order


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = services.create_order(request.user.id, serializer.validated_data)
        return Response(OrderSerializer(order).data, status=201)


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        skip, limit = get_skip_limit(request)
        orders = services.list_user_orders(request.user.id, skip, limit)
        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, order_id: int):
        order = services.get_order(order_id)
        if not order:
            raise NotFound("Order not found")
        if request.user.role != UserRole.ADMIN and order.user_id != request.user.id:
            raise PermissionDenied("Not your order")
        return Response(OrderSerializer(order).data)


class PayOrderView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, order_id: int):
        # The request body is validated before the ownership check runs.
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = _get_owned_order(request, order_id)
        payment = services.pay_order(order, serializer.validated_data)
        return Response(PaymentSerializer(payment).data)


class OrderPaymentsView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, order_id: int):
        _get_owned_order(request, order_id)
        payments = services.get_order_payments(order_id)
        return Response(PaymentSerializer(payments, many=True).data)
