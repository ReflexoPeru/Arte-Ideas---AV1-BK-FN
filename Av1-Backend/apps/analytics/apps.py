"""
Analytics App Configuration - Arte Ideas
"""
from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    verbose_name = 'Analytics'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        # Importar admin para que se registre
        try:
            from . import admin
        except ImportError:
            pass

