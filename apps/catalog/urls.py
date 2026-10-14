from django.urls import path

from apps.catalog import views

urlpatterns = [
    path("brands", views.BrandListView.as_view(), name="brand-list"),
    path("brands/<int:brand_id>", views.BrandDetailView.as_view(), name="brand-detail"),
    path("categories", views.CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<int:category_id>",
        views.CategoryDetailView.as_view(),
        name="category-detail",
    ),
]
