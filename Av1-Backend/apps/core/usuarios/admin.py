"""
Admin del Módulo de Usuarios - Arte Ideas
"""
from django.contrib import admin
from .models import UserProfile, UserActivity


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para perfiles de usuario"""
    list_display = ['user', 'language', 'theme', 'email_notifications', 'created_at']
    list_filter = ['language', 'theme', 'email_notifications', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Preferencias', {
            'fields': ('language', 'theme', 'email_notifications')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin para actividades de usuario"""
    list_display = ['user', 'tenant', 'action', 'module', 'created_at']
    list_filter = ['action', 'module', 'tenant', 'created_at']
    search_fields = ['user__username', 'description', 'module']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'tenant', 'action', 'module')
        }),
        ('Detalles', {
            'fields': ('description', 'ip_address', 'user_agent')
        }),
        ('Fecha', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        """Filtrar actividades según usuario"""
        qs = super().get_queryset(request)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return qs
        elif request.user.is_authenticated and hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
        return qs.none()
    
    def has_add_permission(self, request):
        """No permitir agregar actividades manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir modificar actividades"""
        return False