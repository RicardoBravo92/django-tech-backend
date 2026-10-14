"""Product endpoints.

List/detail are public (with ``search``/``category_id``/``brand_id`` filters);
writes require an admin.
"""
from __future__ import annotations

from django.db.models import Q
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import get_skip_limit
from apps.common.permissions import IsAdmin
from apps.products.models import Product, ProductSpec
from apps.products.serializers import (
    ProductCreateSerializer,
    ProductSerializer,
    ProductUpdateSerializer,
)

_MISSING = object()


def _int_query_param(request, name: str) -> int | None:
    raw = request.query_params.get(name)
    if raw in (None, ""):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValidationError({name: ["A valid integer is required."]})


def _replace_specs(product: Product, specs: list[dict]) -> None:
    product.specs.all().delete()
    ProductSpec.objects.bulk_create(
        [
            ProductSpec(product=product, key=spec["key"], value=spec["value"])
            for spec in specs
        ]
    )


class ProductListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [AllowAny()]

    def get(self, request):
        search = request.query_params.get("search")
        category_id = _int_query_param(request, "category_id")
        brand_id = _int_query_param(request, "brand_id")
        skip, limit = get_skip_limit(request)

        qs = Product.objects.all().order_by("id")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
        if category_id:
            qs = qs.filter(category_id=category_id)
        if brand_id:
            qs = qs.filter(brand_id=brand_id)

        products = qs[skip : skip + limit]
        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        specs = data.pop("specs", [])
        product = Product.objects.create(**data)
        if specs:
            _replace_specs(product, specs)

        return Response(ProductSerializer(product).data, status=201)


class ProductDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAdmin()]
        return [AllowAny()]

    def _get_object(self, product_id: int) -> Product:
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            raise NotFound("Product not found")
        return product

    def get(self, request, product_id: int):
        return Response(ProductSerializer(self._get_object(product_id)).data)

    def patch(self, request, product_id: int):
        product = self._get_object(product_id)

        serializer = ProductUpdateSerializer(
            product, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        validated = dict(serializer.validated_data)
        specs = validated.pop("specs", _MISSING)

        for field, value in validated.items():
            setattr(product, field, value)
        product.save()

        if specs is not _MISSING:
            _replace_specs(product, specs)

        return Response(ProductSerializer(product).data)

    def delete(self, request, product_id: int):
        self._get_object(product_id).delete()
        return Response(status=204)
