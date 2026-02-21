"""
Admin del Módulo de Multi-tenancy - Arte Ideas
"""
from django.contrib import admin
from .models import Tenant, TenantConfiguration


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin para tenants (estudios fotográficos)"""
    list_display = ['name', 'slug', 'business_name', 'location_type', 'is_active', 'created_at']
    list_filter = ['location_type', 'is_active', 'currency', 'created_at']
    search_fields = ['name', 'slug', 'business_name', 'business_email']
    
    # 🟢 CORRECCIÓN: Se eliminó 'slug' de readonly_fields
    readonly_fields = ['created_at', 'updated_at']
    # 🟢 CORRECCIÓN: prepopulated_fields se elimina
    
    fieldsets = (
        ('Información del Estudio', {
            # 🟢 CORRECCIÓN: Se eliminó 'slug' de fields
            'fields': ('name', 'description', 'is_active') 
        }),
        ('Información del Negocio', {
            'fields': (
                'business_name', 'business_address', 'business_phone',
                'business_email', 'business_ruc', 'currency'
            )
        }),
        ('Configuración', {
            'fields': ('location_type', 'max_users', 'max_storage_mb')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filtrar tenants según permisos"""
        qs = super().get_queryset(request)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return qs
        elif request.user.is_authenticated and hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(id=request.user.tenant.id)
        return qs.none()
    
    def has_add_permission(self, request):
        """Solo super admin puede crear tenants"""
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin'
    
    def has_delete_permission(self, request, obj=None):
        """Solo super admin puede eliminar tenants"""
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin'


@admin.register(TenantConfiguration)
class TenantConfigurationAdmin(admin.ModelAdmin):
    # ... (El resto de la clase TenantConfigurationAdmin)
    list_display = ['tenant', 'module', 'key', 'value_preview', 'data_type', 'is_editable']
    list_filter = ['tenant', 'module', 'data_type', 'is_editable']
    search_fields = ['tenant__name', 'key', 'value', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configuración', {
            'fields': ('tenant', 'module', 'key', 'value', 'data_type')
        }),
        ('Metadatos', {
            'fields': ('description', 'is_editable')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def value_preview(self, obj):
        """Mostrar preview del valor"""
        return obj.value[:30] + '...' if len(obj.value) > 30 else obj.value
    value_preview.short_description = 'Valor'
    
    def get_queryset(self, request):
        """Filtrar configuraciones según usuario"""
        qs = super().get_queryset(request)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return qs
        elif request.user.is_authenticated and hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
        return qs.none()