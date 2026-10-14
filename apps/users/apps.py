from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "apps.users"
    label = "users"
    verbose_name = "Users"
    default_auto_field = "django.db.models.AutoField"
