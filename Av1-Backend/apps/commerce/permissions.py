"""
Permisos del Commerce App - Arte Ideas
Permisos centralizados para compatibilidad
"""

# Importar permisos específicos de módulos
from .pedidos.permissions import OrderPermission, OrderItemPermission, OrderPaymentPermission
from .inventario.permissions import InventarioPermission

# Mantener permisos originales para compatibilidad
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permiso personalizado para que solo los propietarios puedan editar"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Super admin puede editar todo
        if request.user.role == 'super_admin':
            return True
        
        # Verificar que el objeto pertenece al tenant del usuario
        if not request.user.tenant:
            return False
        return obj.tenant == request.user.tenant


class CommercePermission(permissions.BasePermission):
    """
    Permisos específicos para el módulo Commerce (Pedidos)
    Basado en roles y permisos del sistema
    """
    
    def has_permission(self, request, view):
        # Usuarios no autenticados no tienen acceso
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admin tiene acceso completo
        if request.user.role == 'super_admin':
            return True
        
        # Verificar permisos específicos del módulo commerce
        required_permissions = self.get_required_permissions(request.method, view)
        
        # Si no hay permisos específicos requeridos, denegar por seguridad
        if not required_permissions:
            return False
        
        # Verificar si el usuario tiene alguno de los permisos requeridos
        user_permissions = request.user.get_permissions_list()
        return any(permission in user_permissions for permission in required_permissions)
    
    def has_object_permission(self, request, view, obj):
        # Primero verificar permisos generales
        if not self.has_permission(request, view):
            return False
        
        # Verificar que el objeto pertenece al tenant del usuario
        # Super admin puede acceder a objetos de cualquier tenant
        if request.user.role != 'super_admin' and hasattr(obj, 'tenant'):
            if request.user.tenant is None or obj.tenant != request.user.tenant:
                return False
        
        # Verificar permisos específicos por acción
        if request.method in permissions.SAFE_METHODS:
            return self.has_read_permission(request, view, obj)
        else:
            return self.has_write_permission(request, view, obj)
    
    def get_required_permissions(self, method, view):
        """
        Obtener los permisos requeridos según el método HTTP y la vista
        """
        # Mapeo de métodos HTTP a permisos necesarios
        permission_map = {
            'GET': ['access:pedidos'],
            'POST': ['access:pedidos'],
            'PUT': ['access:pedidos'],
            'PATCH': ['access:pedidos'],
            'DELETE': ['access:pedidos'],
        }
        
        # Permisos adicionales según la acción de la vista
        if hasattr(view, 'action'):
            action_permissions = {
                'list': ['access:pedidos'],
                'retrieve': ['access:pedidos'],
                'create': ['access:pedidos'],
                'update': ['access:pedidos'],
                'partial_update': ['access:pedidos'],
                'destroy': ['access:pedidos'],
                'summary': ['access:pedidos'],
                'autocomplete': ['access:pedidos'],
                'mark_completed': ['access:pedidos'],
                'mark_cancelled': ['access:pedidos'],
                'overdue': ['access:pedidos'],
                'by_status': ['access:pedidos'],
                'upcoming_deliveries': ['access:pedidos'],
            }
            
            action = view.action
            if action in action_permissions:
                return action_permissions[action]
        
        return permission_map.get(method, [])
    
    def has_read_permission(self, request, view, obj):
        """
        Verificar permisos de lectura según el rol del usuario
        """
        user_role = request.user.role
        
        # Admin y manager pueden ver todos los datos del tenant
        if user_role in ['admin', 'manager']:
            return True
        
        # Employee, photographer y assistant pueden ver datos básicos
        if user_role in ['employee', 'photographer', 'assistant']:
            # Pueden ver pedidos pero no datos financieros sensibles
            if hasattr(view, 'action') and view.action in ['summary']:
                # Solo admin y manager pueden ver resúmenes financieros
                return user_role in ['admin', 'manager']
            return True
        
        return False
    
    def has_write_permission(self, request, view, obj):
        """
        Verificar permisos de escritura según el rol del usuario
        """
        user_role = request.user.role
        
        # Admin tiene control total
        if user_role == 'admin':
            return True
        
        # Manager puede editar pero no eliminar
        if user_role == 'manager':
            return request.method not in ['DELETE']
        
        # Employee puede crear y editar pedidos
        if user_role == 'employee':
            return request.method in ['POST', 'PUT', 'PATCH']
        
        # Photographer y assistant solo lectura
        if user_role in ['photographer', 'assistant']:
            return False
        
        return False


class ProductPermission(permissions.BasePermission):
    """
    Permisos específicos para la gestión de productos (inventario)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'super_admin':
            return True
        
        # Verificar acceso al módulo de inventario
        return 'access:inventario' in request.user.get_permissions_list()
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        if hasattr(obj, 'tenant') and obj.tenant != request.user.tenant:
            return False
        
        user_role = request.user.role
        
        # Lectura permitida para roles con acceso a inventario
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura según rol
        if user_role == 'admin':
            return True
        elif user_role == 'manager':
            return request.method not in ['DELETE']
        elif user_role == 'employee':
            # Employee puede actualizar stock pero no crear/eliminar productos
            return request.method in ['PUT', 'PATCH'] and view.action in ['update_stock']
        
        return False


class OrderItemPermission(permissions.BasePermission):
    """
    Permisos para OrderItem - hereda lógica de Order
    """
    
    def has_permission(self, request, view):
        # Usar los mismos permisos que para Order
        commerce_perm = CommercePermission()
        return commerce_perm.has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        
        # Verificar a través del pedido padre
        if request.user.role != 'super_admin' and hasattr(obj, 'order'):
            if request.user.tenant is None or obj.order.tenant != request.user.tenant:
                return False
        
        # Usar la misma lógica que Order
        commerce_perm = CommercePermission()
        return commerce_perm.has_write_permission(request, view, obj.order)