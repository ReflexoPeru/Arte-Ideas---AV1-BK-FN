"""
CRM App Configuration - Arte Ideas
"""
from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm'
    verbose_name = 'CRM'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        pass