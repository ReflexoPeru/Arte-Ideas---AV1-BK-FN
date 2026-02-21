"""
URLs del Módulo de Configuración del Sistema - Arte Ideas
"""
from django.urls import path
from .views import (
    BusinessConfigurationView, UsersManagementView, UserManagementDetailView,
    RolesListView, RolePermissionsView, TenantsManagementView, TenantUsersView
)

app_name = 'configuracion_sistema'

urlpatterns = [
    # Configuración del negocio
    path('business/', BusinessConfigurationView.as_view(), name='business_config'),
    
    # Gestión de usuarios
    path('users/', UsersManagementView.as_view(), name='users_management'),
    path('users/<int:user_id>/', UserManagementDetailView.as_view(), name='user_detail'),
    
    # Roles y permisos
    path('roles/', RolesListView.as_view(), name='roles_list'),
    path('permissions/', RolePermissionsView.as_view(), name='permissions_list'),
    path('permissions/<str:role>/', RolePermissionsView.as_view(), name='role_permissions'),
    
    # Super admin - gestión de tenants
    path('tenants/', TenantsManagementView.as_view(), name='tenants_management'),
    path('tenants/<int:tenant_id>/users/', TenantUsersView.as_view(), name='tenant_users'),
]