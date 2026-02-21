"""
Configuración de la aplicación Activos - Arte Ideas Operations
"""
from django.apps import AppConfig


class ActivosConfig(AppConfig):
    """Configuración del módulo de Activos"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.operations.activos'
    verbose_name = 'Activos'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        # Importar señales si las hay
        try:
            from . import signals
        except ImportError:
            pass
