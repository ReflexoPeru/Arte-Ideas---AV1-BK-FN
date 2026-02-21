from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core - Sistema Base (Arquitectura Modular)'
    
    def ready(self):
        """
        Código que se ejecuta cuando la app está lista
        Importar signals de todos los módulos
        """
        # Importar signals de los módulos reorganizados
        try:
            from . import signals  # Signals generales si existen
        except ImportError:
            pass
        
        try:
            from .autenticacion import signals as auth_signals
        except ImportError:
            pass
            
        try:
            from .usuarios import signals as user_signals
        except ImportError:
            pass