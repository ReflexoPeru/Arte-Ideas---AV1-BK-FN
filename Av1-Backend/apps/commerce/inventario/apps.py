"""
Configuración de la aplicación Inventario - Arte Ideas Commerce
"""
from django.apps import AppConfig


class InventarioConfig(AppConfig):
    """Configuración del módulo de Inventario"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.commerce.inventario'
    verbose_name = 'Inventario'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        # Importar señales del módulo
        try:
            from . import signals
        except ImportError:
            pass