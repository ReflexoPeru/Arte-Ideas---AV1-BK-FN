"""
Analytics Admin - Arte Ideas
"""
from django.contrib import admin
from .models import ReportConfiguration


@admin.register(ReportConfiguration)
class ReportConfigurationAdmin(admin.ModelAdmin):
    """
    Admin para configuraciones de reportes
    """
    list_display = ['nombre', 'categoria', 'dias_por_defecto', 'activo', 'created_at']
    list_filter = ['categoria', 'activo', 'created_at']
    search_fields = ['nombre', 'descripcion', 'categoria']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('dias_por_defecto', 'activo')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Importar admin de Reportes si existe
try:
    from .Reportes import admin as reportes_admin
except ImportError:
    pass

