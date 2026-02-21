"""
Views del Módulo de Configuración del Sistema - Arte Ideas
Gestión de usuarios, permisos y configuraciones del negocio
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from apps.core.multitenancy.models import Tenant
from apps.core.usuarios.models import UserActivity
from apps.core.autenticacion.models import RolePermission

from .serializers import (
    TenantSerializer, RolePermissionSerializer, UserManagementSerializer,
    CreateUserSerializer, SuperAdminTenantSerializer
)

User = get_user_model()


class BusinessConfigurationView(APIView):
    """Vista para configuración del negocio"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener configuración del negocio"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = TenantSerializer(request.user.tenant)
        return Response(serializer.data)
    
    def put(self, request):
        """Actualizar configuración del negocio"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede modificar configuración del negocio
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para modificar configuración'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = TenantSerializer(request.user.tenant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Registrar actividad
            UserActivity.objects.create(
                user=request.user,
                tenant=request.user.tenant,
                action='config_change',
                description='Actualizó la configuración del negocio',
                module='configuration'
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersManagementView(APIView):
    """Vista para gestión de usuarios del tenant"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener lista de usuarios del tenant"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede ver usuarios
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para ver usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.filter(tenant=request.user.tenant).exclude(id=request.user.id)
        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Crear nuevo usuario en el tenant"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede crear usuarios
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para crear usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = CreateUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            
            # Registrar actividad
            UserActivity.objects.create(
                user=request.user,
                tenant=request.user.tenant,
                action='create',
                description=f'Creó el usuario {user.username}',
                module='users'
            )
            
            return Response(UserManagementSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserManagementDetailView(APIView):
    """Vista para gestión individual de usuarios"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        """Obtener datos de un usuario específico"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede ver usuarios
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para ver usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserManagementSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, user_id):
        """Actualizar usuario específico"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede modificar usuarios
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para modificar usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserManagementSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Registrar actividad
            UserActivity.objects.create(
                user=request.user,
                tenant=request.user.tenant,
                action='update',
                description=f'Actualizó el usuario {user.username}',
                module='users'
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, user_id):
        """Activar/Desactivar usuario"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede activar/desactivar usuarios
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para modificar usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = not user.is_active
        user.save()
        
        action = 'activó' if user.is_active else 'desactivó'
        
        # Registrar actividad
        UserActivity.objects.create(
            user=request.user,
            tenant=request.user.tenant,
            action='update',
            description=f'{action.capitalize()} el usuario {user.username}',
            module='users'
        )
        
        return Response({
            'message': f'Usuario {action} correctamente',
            'is_active': user.is_active
        })
    
    def delete(self, request, user_id):
        """Eliminar usuario (soft delete)"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede eliminar usuarios
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para eliminar usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # No permitir eliminar al usuario actual
        if user.id == request.user.id:
            return Response({'error': 'No puedes eliminar tu propio usuario'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        username = user.username
        user.delete()
        
        # Registrar actividad
        UserActivity.objects.create(
            user=request.user,
            tenant=request.user.tenant,
            action='delete',
            description=f'Eliminó el usuario {username}',
            module='users'
        )
        
        return Response({'message': f'Usuario {username} eliminado correctamente'})


class RolesListView(APIView):
    """Vista para obtener lista de roles disponibles"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener lista de roles disponibles"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede ver roles
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para ver roles'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        roles = []
        for role_code, role_name in User.ROLE_CHOICES:
            if role_code != 'super_admin':  # No mostrar super_admin en la lista
                roles.append({
                    'code': role_code,
                    'name': role_name
                })
        
        return Response(roles)


class RolePermissionsView(APIView):
    """Vista para gestión de permisos por rol"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, role=None):
        """Obtener permisos de un rol específico o todos los roles"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede ver permisos
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para ver permisos'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if role:
            try:
                permission = RolePermission.objects.get(tenant=request.user.tenant, role=role)
                serializer = RolePermissionSerializer(permission)
                return Response(serializer.data)
            except RolePermission.DoesNotExist:
                return Response({'error': 'Permisos no encontrados'}, 
                              status=status.HTTP_404_NOT_FOUND)
        else:
            permissions = RolePermission.objects.filter(tenant=request.user.tenant)
            serializer = RolePermissionSerializer(permissions, many=True)
            return Response(serializer.data)
    
    def put(self, request, role):
        """Actualizar permisos de un rol"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede modificar permisos
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para modificar permisos'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            permission = RolePermission.objects.get(tenant=request.user.tenant, role=role)
        except RolePermission.DoesNotExist:
            return Response({'error': 'Permisos no encontrados'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        serializer = RolePermissionSerializer(permission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Registrar actividad
            UserActivity.objects.create(
                user=request.user,
                tenant=request.user.tenant,
                action='config_change',
                description=f'Actualizó permisos del rol {role}',
                module='permissions'
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, role):
        """Restablecer permisos por defecto"""
        if not request.user.tenant:
            return Response({'error': 'Usuario no pertenece a un tenant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Solo admin puede restablecer permisos
        if request.user.role not in ['admin', 'super_admin']:
            return Response({'error': 'Sin permisos para restablecer permisos'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            permission = RolePermission.objects.get(tenant=request.user.tenant, role=role)
        except RolePermission.DoesNotExist:
            return Response({'error': 'Permisos no encontrados'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Aplicar permisos por defecto
        defaults = RolePermission.get_default_permissions(role)
        for field, value in defaults.items():
            setattr(permission, field, value)
        permission.save()
        
        # Registrar actividad
        UserActivity.objects.create(
            user=request.user,
            tenant=request.user.tenant,
            action='config_change',
            description=f'Restableció permisos por defecto del rol {role}',
            module='permissions'
        )
        
        serializer = RolePermissionSerializer(permission)
        return Response(serializer.data)


# Vistas para super admin - gestión de tenants
class TenantsManagementView(APIView):
    """Vista para gestión de tenants (solo super admin)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener lista de todos los tenants"""
        if request.user.role != 'super_admin':
            return Response({'error': 'Solo super admin puede ver tenants'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        tenants = Tenant.objects.all()
        serializer = SuperAdminTenantSerializer(tenants, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Crear nuevo tenant"""
        if request.user.role != 'super_admin':
            return Response({'error': 'Solo super admin puede crear tenants'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            tenant = serializer.save()
            return Response(SuperAdminTenantSerializer(tenant).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantUsersView(APIView):
    """Vista para ver usuarios de un tenant específico (solo super admin)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, tenant_id):
        """Obtener usuarios de un tenant específico"""
        if request.user.role != 'super_admin':
            return Response({'error': 'Solo super admin puede ver usuarios de tenants'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant no encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        users = User.objects.filter(tenant=tenant)
        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data)