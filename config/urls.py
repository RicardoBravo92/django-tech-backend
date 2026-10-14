"""Root URL configuration.

Route layout (all paths are trailing-slash
free, e.g. ``/api/v1/brands``).
"""
from django.urls import include, path

from apps.common.views import HealthView

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/", include("apps.products.urls")),
    path("api/v1/", include("apps.orders.urls")),
    path("api/v1/", include("apps.warehouses.urls")),
    path("api/v1/", include("apps.reports.urls")),
]
