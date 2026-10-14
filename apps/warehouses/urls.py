from django.urls import path

from apps.warehouses import views

urlpatterns = [
    path("warehouses", views.WarehouseListView.as_view(), name="warehouse-list"),
    path(
        "warehouses/products/<int:product_id>/stock",
        views.ProductStockView.as_view(),
        name="warehouse-product-stock",
    ),
    path(
        "warehouses/<int:warehouse_id>",
        views.WarehouseDetailView.as_view(),
        name="warehouse-detail",
    ),
]
