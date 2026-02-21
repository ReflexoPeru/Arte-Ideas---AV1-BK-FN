"""
CRM Contratos App Configuration - Arte Ideas
"""
from django.apps import AppConfig


class ContratosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm.contratos'
    verbose_name = 'CRM - Contratos'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        pass