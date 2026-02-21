"""
Permisos del Módulo de Activos - Arte Ideas Operations
"""
from rest_framework import permissions


class ActivosPermission(permissions.BasePermission):
    """Permisos específicos para gestión de activos"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'super_admin':
            return True
        
        # Verificar acceso al módulo de activos
        user_permissions = getattr(request.user, 'get_permissions_list', lambda: [])()
        return 'access:activos' in user_permissions or 'access:operations' in user_permissions
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        # Verificar que el objeto pertenece al tenant del usuario (si aplica)
        if hasattr(obj, 'tenant') and obj.tenant != request.user.tenant:
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
        elif user_role in ['employee', 'operario']:
            # Empleados y operarios pueden actualizar pero no crear/eliminar
            return request.method in ['PUT', 'PATCH']
        
        return False


class MantenimientoPermission(permissions.BasePermission):
    """Permisos específicos para mantenimientos"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'super_admin':
            return True
        
        # Operarios pueden gestionar mantenimientos
        user_permissions = getattr(request.user, 'get_permissions_list', lambda: [])()
        return ('access:mantenimiento' in user_permissions or 
                'access:operations' in user_permissions or
                request.user.role == 'operario')
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        user_role = request.user.role
        
        # Lectura permitida para todos con acceso
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Operarios pueden gestionar sus mantenimientos
        if user_role == 'operario':
            return True
        elif user_role in ['admin', 'manager']:
            return True
        
        return False


class RepuestosPermission(permissions.BasePermission):
    """Permisos específicos para repuestos"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'super_admin':
            return True
        
        # Verificar acceso al módulo de repuestos/inventario
        user_permissions = getattr(request.user, 'get_permissions_list', lambda: [])()
        return ('access:repuestos' in user_permissions or 
                'access:inventario' in user_permissions or
                'access:operations' in user_permissions)
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        user_role = request.user.role
        
        # Lectura permitida para todos con acceso
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura según rol
        if user_role == 'admin':
            return True
        elif user_role == 'manager':
            return request.method not in ['DELETE']
        elif user_role in ['employee', 'operario']:
            # Pueden actualizar stock pero no crear/eliminar repuestos
            return request.method in ['PUT', 'PATCH'] and hasattr(view, 'action') and view.action in ['update', 'partial_update', 'actualizar_stock']
        
        return False