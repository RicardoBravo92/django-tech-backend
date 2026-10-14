from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = "apps.products"
    label = "products"
    verbose_name = "Products"
    default_auto_field = "django.db.models.AutoField"
