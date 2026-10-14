from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    brand = models.ForeignKey(
        "catalog.Brand",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    category = models.ForeignKey(
        "catalog.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"

    def __str__(self) -> str:
        return self.name


class ProductSpec(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="specs",
    )
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "product_specs"

    def __str__(self) -> str:
        return f"{self.key}={self.value}"


class ProductStock(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = "product_stocks"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "warehouse"],
                name="uq_product_warehouse",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product_id}@{self.warehouse_id}={self.quantity}"
