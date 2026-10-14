"""Catalog serializers.

Plain ``Serializer`` classes are used (instead of ``ModelSerializer``) for full
control over the JSON shape -- including ``_id`` foreign-key fields such as
``parent_id``.
"""
from rest_framework import serializers

from apps.catalog.models import Brand, Category


class BrandSerializer(serializers.Serializer):
    """Brand read model (id, name, slug)."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)


class BrandCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)


class BrandUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    slug = serializers.CharField(max_length=255, required=False)


class CategorySerializer(serializers.Serializer):
    """Category read model (id, name, slug, description, parent_id)."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_null=True, required=False)
    parent_id = serializers.IntegerField(allow_null=True, required=False)


class CategoryCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=255)
    description = serializers.CharField(
        allow_null=True, required=False, default=None
    )
    parent_id = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )


class CategoryUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    slug = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(allow_null=True, required=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
