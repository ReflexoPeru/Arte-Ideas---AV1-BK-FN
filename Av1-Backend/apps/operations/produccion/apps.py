"""
Configuración de la aplicación Producción - Arte Ideas Operations
"""
from django.apps import AppConfig


class ProduccionConfig(AppConfig):
    """Configuración del módulo de Producción"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.operations.produccion'
    verbose_name = 'Producción'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        # Importar señales si las hay
        try:
            from . import signals
        except ImportError:
            pass