from django.urls import path

from apps.products import views

urlpatterns = [
    path("products", views.ProductListView.as_view(), name="product-list"),
    path(
        "products/<int:product_id>",
        views.ProductDetailView.as_view(),
        name="product-detail",
    ),
]
