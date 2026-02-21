"""
Commerce App Configuration - Arte Ideas
"""
from django.apps import AppConfig


class CommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.commerce'
    verbose_name = 'Commerce'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        try:
            import apps.commerce.signals
        except ImportError:
            pass