"""
Permisos del Operations App - Arte Ideas
Permisos centralizados para compatibilidad
"""

# Importar permisos de producción
from .produccion.permissions import IsSameInquilino, IsSameInmobiliaria

# Importar permisos de activos
from .activos.permissions import (
    ActivosPermission, MantenimientoPermission, RepuestosPermission
)

# Mantener permisos originales para compatibilidad
from rest_framework import permissions


class OperationsPermission(permissions.BasePermission):
    """Permiso general para el módulo Operations"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'super_admin':
            return True
        
        # Verificar acceso al módulo de operations
        user_permissions = getattr(request.user, 'get_permissions_list', lambda: [])()
        return 'access:operations' in user_permissions
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        # Verificar tenant si aplica
        if hasattr(obj, 'tenant') and obj.tenant != request.user.tenant:
            return False
        if hasattr(obj, 'id_inquilino') and obj.id_inquilino != request.user.tenant:
            return False
        
        return True


# Exportar para compatibilidad
__all__ = [
    'IsSameInquilino', 'IsSameInmobiliaria',
    'ActivosPermission', 'MantenimientoPermission', 'RepuestosPermission',
    'OperationsPermission'
]