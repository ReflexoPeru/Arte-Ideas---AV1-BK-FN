"""
Configuración de la aplicación Pedidos - Arte Ideas Commerce
"""
from django.apps import AppConfig


class PedidosConfig(AppConfig):
    """Configuración del módulo de Pedidos"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.commerce.pedidos'
    verbose_name = 'Pedidos'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        # Importar señales del módulo
        try:
            from . import signals
        except ImportError:
            pass