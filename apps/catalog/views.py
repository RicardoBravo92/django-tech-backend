"""Category + Brand endpoints.

List/detail are public; create/update/delete require an admin.
"""
from __future__ import annotations

from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Brand, Category
from apps.catalog.serializers import (
    BrandCreateSerializer,
    BrandSerializer,
    BrandUpdateSerializer,
    CategoryCreateSerializer,
    CategorySerializer,
    CategoryUpdateSerializer,
)
from apps.common.pagination import get_skip_limit
from apps.common.permissions import IsAdmin


class BrandListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [AllowAny()]

    def get(self, request):
        skip, limit = get_skip_limit(request)
        brands = Brand.objects.order_by("id")[skip : skip + limit]
        return Response(BrandSerializer(brands, many=True).data)

    def post(self, request):
        serializer = BrandCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        brand = Brand.objects.create(**serializer.validated_data)
        return Response(BrandSerializer(brand).data, status=201)


class BrandDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAdmin()]
        return [AllowAny()]

    def _get_object(self, brand_id: int) -> Brand:
        brand = Brand.objects.filter(pk=brand_id).first()
        if not brand:
            raise NotFound("Brand not found")
        return brand

    def get(self, request, brand_id: int):
        return Response(BrandSerializer(self._get_object(brand_id)).data)

    def patch(self, request, brand_id: int):
        brand = self._get_object(brand_id)
        serializer = BrandUpdateSerializer(
            brand, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(brand, field, value)
        brand.save()
        return Response(BrandSerializer(brand).data)

    def delete(self, request, brand_id: int):
        self._get_object(brand_id).delete()
        return Response(status=204)


class CategoryListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [AllowAny()]

    def get(self, request):
        skip, limit = get_skip_limit(request)
        categories = Category.objects.order_by("id")[skip : skip + limit]
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = Category.objects.create(**serializer.validated_data)
        return Response(CategorySerializer(category).data, status=201)


class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAdmin()]
        return [AllowAny()]

    def _get_object(self, category_id: int) -> Category:
        category = Category.objects.filter(pk=category_id).first()
        if not category:
            raise NotFound("Category not found")
        return category

    def get(self, request, category_id: int):
        return Response(CategorySerializer(self._get_object(category_id)).data)

    def patch(self, request, category_id: int):
        category = self._get_object(category_id)
        serializer = CategoryUpdateSerializer(
            category, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(category, field, value)
        category.save()
        return Response(CategorySerializer(category).data)

    def delete(self, request, category_id: int):
        self._get_object(category_id).delete()
        return Response(status=204)
