from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = "apps.accounts"        # ← полный путь включая "apps."
    default_auto_field = "django.db.models.BigAutoField"