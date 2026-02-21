"""
Admin del Core App - Arte Ideas
Importaciones centralizadas de todos los módulos admin

NOTA: Los admins específicos están organizados en:
- autenticacion/admin.py - Usuarios y permisos
- usuarios/admin.py - Perfiles y actividades
- configuracion_sistema/admin.py - Configuraciones globales
- multitenancy/admin.py - Tenants y configuraciones específicas

Este archivo mantiene compatibilidad con el admin existente mientras
se migra gradualmente a la nueva estructura modular.
"""
from django.contrib import admin
from django.contrib import messages

# Importar todos los admins para que se registren automáticamente
from .autenticacion import admin as auth_admin
from .usuarios import admin as users_admin
from .configuracion_sistema import admin as config_admin
from .multitenancy import admin as tenant_admin

# Personalización del admin site
admin.site.site_header = "Arte Ideas - Administración (Estructura Reorganizada)"
admin.site.site_title = "Arte Ideas Admin"
admin.site.index_title = "Panel de Administración - Arquitectura Modular"

# Acción personalizada para cambiar contexto de tenant (solo super admin)
def switch_tenant_context(modeladmin, request, queryset):
    """Acción para cambiar contexto de tenant"""
    if not request.user.is_authenticated or not hasattr(request.user, 'role') or request.user.role != 'super_admin':
        messages.error(request, "Solo super admin puede cambiar contexto de tenant")
        return
    
    if queryset.count() != 1:
        messages.error(request, "Selecciona exactamente un tenant")
        return
    
    tenant = queryset.first()
    # Aquí se implementaría la lógica para cambiar contexto
    # Por ahora solo mostramos un mensaje
    messages.success(request, f"Contexto cambiado a: {tenant.name}")

switch_tenant_context.short_description = "Cambiar contexto de tenant"