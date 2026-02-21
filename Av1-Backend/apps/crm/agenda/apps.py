from django.apps import AppConfig


class AgendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm.agenda'
    verbose_name = 'Agenda CRM'

    def ready(self):
        # Importar señales cuando la app está lista
        from . import signals  # noqa