"""
Permisos del Módulo de Inventario - Arte Ideas Commerce
"""
from rest_framework import permissions


class InventarioPermission(permissions.BasePermission):
    """Permisos específicos para inventario"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'super_admin':
            return True
        
        # Verificar acceso al módulo de inventario
        user_permissions = getattr(request.user, 'get_permissions_list', lambda: [])()
        return 'access:inventario' in user_permissions
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        # Verificar que el objeto pertenece al tenant del usuario
        # Super admin puede acceder a objetos de cualquier tenant
        if request.user.role != 'super_admin' and hasattr(obj, 'tenant'):
            if request.user.tenant is None or obj.tenant != request.user.tenant:
                return False
        
        user_role = request.user.role
        
        # Lectura permitida para todos los roles con acceso
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura según rol
        if user_role == 'admin':
            return True
        elif user_role == 'manager':
            return request.method not in ['DELETE']
        elif user_role == 'employee':
            # Employee puede actualizar stock pero no crear/eliminar productos
            return request.method in ['PUT', 'PATCH'] and hasattr(view, 'action') and view.action in ['update', 'partial_update']
        
        return False


class ProductPermission(InventarioPermission):
    """Alias para compatibilidad"""
    pass