# File: menus/apps.py
from django.apps import AppConfig

class MenusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'menus'

    def ready(self):
        import menus.signals # Import the signals module