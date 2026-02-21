"""
Operations App Configuration - Arte Ideas
"""
from django.apps import AppConfig


class OperationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.operations'
    verbose_name = 'Operations'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        pass