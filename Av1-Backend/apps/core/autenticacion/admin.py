"""
Admin del Módulo de Autenticación - Arte Ideas
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import RolePermission

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin para modelo User"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'tenant', 'is_active']
    list_filter = ['role', 'tenant', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información del Estudio', {
            'fields': ('tenant', 'role', 'phone', 'avatar')
        }),
        ('Información Adicional', {
            'fields': ('address', 'bio', 'is_new_user', 'email_verified')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Filtrar usuarios según permisos"""
        qs = super().get_queryset(request)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return qs
        elif request.user.is_authenticated and hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
        return qs.none()


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin para permisos de roles"""
    list_display = ['tenant', 'role', 'access_dashboard', 'access_pedidos', 'view_precios']
    list_filter = ['tenant', 'role']
    search_fields = ['tenant__name', 'role']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tenant', 'role')
        }),
        ('Acceso a Módulos', {
            'fields': (
                'access_dashboard', 'access_agenda', 'access_pedidos', 'access_clientes',
                'access_inventario', 'access_activos', 'access_gastos', 'access_produccion',
                'access_contratos', 'access_reportes'
            )
        }),
        ('Acciones Sensibles', {
            'fields': (
                'view_costos', 'view_precios', 'view_margenes', 'view_datos_clientes',
                'view_datos_financieros', 'edit_precios', 'delete_registros'
            )
        }),
    )
    
    def get_queryset(self, request):
        """Filtrar permisos según usuario"""
        qs = super().get_queryset(request)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return qs
        elif request.user.is_authenticated and hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
        return qs.none()