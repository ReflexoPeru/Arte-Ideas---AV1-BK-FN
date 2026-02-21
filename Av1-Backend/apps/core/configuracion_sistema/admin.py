"""
Admin del Módulo de Configuración del Sistema - Arte Ideas
"""
from django.contrib import admin
from .models import SystemConfiguration


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """Admin para configuraciones del sistema"""
    list_display = ['key', 'value_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configuración', {
            'fields': ('key', 'value', 'description', 'is_active')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def value_preview(self, obj):
        """Mostrar preview del valor"""
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Valor'
    
    def has_module_permission(self, request):
        """Solo super admin puede ver configuraciones del sistema"""
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin'