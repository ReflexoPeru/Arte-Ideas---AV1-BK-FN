"""
Permisos del Módulo de Pedidos - Arte Ideas Commerce
"""
from rest_framework import permissions


class OrderPermission(permissions.BasePermission):
    """Permisos específicos para pedidos"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'super_admin':
            return True
        
        # Verificar acceso al módulo de pedidos
        user_permissions = getattr(request.user, 'get_permissions_list', lambda: [])()
        return 'access:pedidos' in user_permissions
    
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
            return request.method in ['POST', 'PUT', 'PATCH']
        
        return False


class OrderItemPermission(permissions.BasePermission):
    """Permisos para items de pedido"""
    
    def has_permission(self, request, view):
        order_perm = OrderPermission()
        return order_perm.has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        # Verificar a través del pedido padre
        if hasattr(obj, 'order'):
            order_perm = OrderPermission()
            return order_perm.has_object_permission(request, view, obj.order)
        
        return False


class OrderPaymentPermission(permissions.BasePermission):
    """Permisos para pagos de pedido"""
    
    def has_permission(self, request, view):
        order_perm = OrderPermission()
        return order_perm.has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        # Verificar a través del pedido padre
        if hasattr(obj, 'order'):
            order_perm = OrderPermission()
            return order_perm.has_object_permission(request, view, obj.order)
        
        return False