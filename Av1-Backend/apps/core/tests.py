"""
Tests del Core App - Arte Ideas
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Tenant, UserProfile, RolePermission

User = get_user_model()


class TenantModelTest(TestCase):
    """Tests para el modelo Tenant"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Studio",
            business_name="Test Business",
            business_address="Test Address",
            business_phone="123456789",
            business_email="test@test.com",
            business_ruc="12345678901",
            location_type="lima"
        )
    
    def test_tenant_creation(self):
        """Test creación de tenant"""
        self.assertEqual(self.tenant.name, "Test Studio")
        self.assertTrue(self.tenant.has_global_data_access())
        self.assertTrue(self.tenant.has_financial_modules())
    
    def test_tenant_slug_generation(self):
        """Test generación automática de slug"""
        self.assertIsNotNone(self.tenant.slug)


class UserModelTest(TestCase):
    """Tests para el modelo User"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Studio",
            business_name="Test Business",
            business_address="Test Address",
            business_phone="123456789",
            business_email="test@test.com",
            business_ruc="12345678901"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            tenant=self.tenant,
            role="operario"
        )
    
    def test_user_creation(self):
        """Test creación de usuario"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.tenant, self.tenant)
        self.assertEqual(self.user.role, "operario")
    
    def test_user_permissions(self):
        """Test sistema de permisos"""
        permissions = self.user.get_permissions_list()
        self.assertIn('access:dashboard', permissions)
        self.assertTrue(self.user.has_permission('access:dashboard'))


class AuthenticationAPITest(APITestCase):
    """Tests para autenticación JWT"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Studio",
            business_name="Test Business",
            business_address="Test Address",
            business_phone="123456789",
            business_email="test@test.com",
            business_ruc="12345678901"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            tenant=self.tenant,
            role="admin"
        )
        
        # Crear perfil
        UserProfile.objects.create(user=self.user)
    
    def test_login(self):
        """Test login JWT"""
        url = reverse('core:authentication:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_profile_access(self):
        """Test acceso al perfil"""
        # Obtener token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:profile:profile_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')


class ProfileAPITest(APITestCase):
    """Tests para APIs de perfil"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Studio",
            business_name="Test Business",
            business_address="Test Address",
            business_phone="123456789",
            business_email="test@test.com",
            business_ruc="12345678901"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            tenant=self.tenant,
            role="admin"
        )
        
        UserProfile.objects.create(user=self.user)
        
        # Autenticar
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_get_profile_statistics(self):
        """Test obtener estadísticas del perfil"""
        url = reverse('core:profile:statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('orders_processed', response.data)
        self.assertIn('clients_attended', response.data)
    
    def test_change_password(self):
        """Test cambio de contraseña"""
        url = reverse('core:profile:change_password')
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ConfigurationAPITest(APITestCase):
    """Tests para APIs de configuración"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Studio",
            business_name="Test Business",
            business_address="Test Address",
            business_phone="123456789",
            business_email="test@test.com",
            business_ruc="12345678901"
        )
        
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="adminpass123",
            tenant=self.tenant,
            role="admin"
        )
        
        self.employee_user = User.objects.create_user(
            username="employee",
            email="employee@test.com",
            password="emppass123",
            tenant=self.tenant,
            role="ventas"
        )
        
        UserProfile.objects.create(user=self.admin_user)
        UserProfile.objects.create(user=self.employee_user)
        
        # Crear permisos por defecto
        RolePermission.objects.create(
            tenant=self.tenant,
            role="admin",
            **RolePermission.get_default_permissions("admin")
        )
    
    def test_business_config_access_admin(self):
        """Test acceso a configuración del negocio como admin"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:configuration:business_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Studio')
    
    def test_business_config_access_ventas(self):
        """Test acceso denegado a configuración como ventas"""
        refresh = RefreshToken.for_user(self.employee_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:configuration:business_edit')
        response = self.client.put(url, {'business_name': 'New Name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_users_management(self):
        """Test gestión de usuarios"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:configuration:users_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe mostrar solo el employee (no el admin actual)
        self.assertEqual(len(response.data), 1)


class MultiTenancyTest(APITestCase):
    """Tests para aislamiento multi-tenant"""
    
    def setUp(self):
        # Tenant A
        self.tenant_a = Tenant.objects.create(
            name="Studio A",
            business_name="Business A",
            business_address="Address A",
            business_phone="111111111",
            business_email="a@test.com",
            business_ruc="11111111111"
        )
        
        # Tenant B
        self.tenant_b = Tenant.objects.create(
            name="Studio B",
            business_name="Business B",
            business_address="Address B",
            business_phone="222222222",
            business_email="b@test.com",
            business_ruc="22222222222"
        )
        
        # Usuario de Tenant A
        self.user_a = User.objects.create_user(
            username="user_a",
            email="user_a@test.com",
            password="pass123",
            tenant=self.tenant_a,
            role="admin"
        )
        
        # Usuario de Tenant B
        self.user_b = User.objects.create_user(
            username="user_b",
            email="user_b@test.com",
            password="pass123",
            tenant=self.tenant_b,
            role="admin"
        )
        
        UserProfile.objects.create(user=self.user_a)
        UserProfile.objects.create(user=self.user_b)
    
    def test_tenant_isolation(self):
        """Test aislamiento entre tenants"""
        # Usuario A no debe ver usuarios de Tenant B
        refresh = RefreshToken.for_user(self.user_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:configuration:users_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # No debe haber usuarios (solo ve usuarios de su tenant, excluyendo a sí mismo)
        self.assertEqual(len(response.data), 0)
    
    def test_business_config_isolation(self):
        """Test aislamiento de configuración de negocio"""
        refresh = RefreshToken.for_user(self.user_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:configuration:business_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Studio A')
        self.assertNotEqual(response.data['name'], 'Studio B')


class HU01RoleManagementTest(TestCase):
    """Tests específicos para roles según HU01"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Studio",
            business_name="Test Business",
            business_address="Test Address",
            business_phone="123456789",
            business_email="test@test.com",
            business_ruc="12345678901"
        )
    
    def test_hu01_role_choices(self):
        """Test que solo existen los roles especificados en HU01"""
        expected_roles = ['super_admin', 'admin', 'ventas', 'produccion', 'operario']
        actual_roles = [choice[0] for choice in User.ROLE_CHOICES]
        
        self.assertEqual(set(actual_roles), set(expected_roles))
        self.assertEqual(len(actual_roles), 5)
    
    def test_old_roles_not_available(self):
        """Test que los roles antiguos ya no están disponibles"""
        old_roles = ['manager', 'employee', 'photographer', 'assistant']
        actual_roles = [choice[0] for choice in User.ROLE_CHOICES]
        
        for old_role in old_roles:
            self.assertNotIn(old_role, actual_roles)
    
    def test_default_role_is_operario(self):
        """Test que el rol por defecto es operario"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            tenant=self.tenant
            # No especificar role para usar el default
        )
        self.assertEqual(user.role, 'operario')
    
    def test_ventas_role_permissions(self):
        """Test permisos del rol ventas según HU01"""
        user = User.objects.create_user(
            username="ventas_user",
            email="ventas@test.com",
            password="testpass123",
            tenant=self.tenant,
            role="ventas"
        )
        
        permissions = user.get_permissions_list()
        
        # Debe tener acceso a módulos de ventas
        self.assertIn('access:dashboard', permissions)
        self.assertIn('access:agenda', permissions)
        self.assertIn('access:pedidos', permissions)
        self.assertIn('access:clientes', permissions)
        self.assertIn('access:contratos', permissions)
        
        # No debe tener acceso a módulos de producción
        self.assertNotIn('access:produccion', permissions)
        self.assertNotIn('access:inventario', permissions)
        self.assertNotIn('access:activos', permissions)
    
    def test_produccion_role_permissions(self):
        """Test permisos del rol producción según HU01"""
        user = User.objects.create_user(
            username="produccion_user",
            email="produccion@test.com",
            password="testpass123",
            tenant=self.tenant,
            role="produccion"
        )
        
        permissions = user.get_permissions_list()
        
        # Debe tener acceso a módulos de producción
        self.assertIn('access:dashboard', permissions)
        self.assertIn('access:produccion', permissions)
        self.assertIn('access:inventario', permissions)
        self.assertIn('access:activos', permissions)
        
        # No debe tener acceso a módulos financieros
        self.assertNotIn('access:gastos', permissions)
        self.assertNotIn('access:contratos', permissions)
    
    def test_operario_role_permissions(self):
        """Test permisos del rol operario según HU01"""
        user = User.objects.create_user(
            username="operario_user",
            email="operario@test.com",
            password="testpass123",
            tenant=self.tenant,
            role="operario"
        )
        
        permissions = user.get_permissions_list()
        
        # Debe tener acceso básico
        self.assertIn('access:dashboard', permissions)
        self.assertIn('access:agenda', permissions)
        self.assertIn('access:produccion', permissions)
        
        # No debe tener acceso a módulos administrativos
        self.assertNotIn('access:gastos', permissions)
        self.assertNotIn('access:activos', permissions)
        self.assertNotIn('access:contratos', permissions)
        self.assertNotIn('access:reportes', permissions)
    
    def test_admin_role_maintains_full_access(self):
        """Test que el rol admin mantiene acceso completo"""
        user = User.objects.create_user(
            username="admin_user",
            email="admin@test.com",
            password="testpass123",
            tenant=self.tenant,
            role="admin"
        )
        
        permissions = user.get_permissions_list()
        
        # Debe tener acceso a todos los módulos
        expected_modules = [
            'access:dashboard', 'access:agenda', 'access:pedidos', 'access:clientes',
            'access:inventario', 'access:activos', 'access:gastos', 'access:produccion',
            'access:contratos', 'access:reportes', 'access:configuration'
        ]
        
        for module in expected_modules:
            self.assertIn(module, permissions)
    
    def test_role_permission_default_mapping(self):
        """Test mapeo de permisos por defecto para nuevos roles"""
        # Test ventas
        ventas_defaults = RolePermission.get_default_permissions('ventas')
        self.assertTrue(ventas_defaults['access_dashboard'])
        self.assertTrue(ventas_defaults['access_clientes'])
        self.assertTrue(ventas_defaults['access_pedidos'])
        self.assertFalse(ventas_defaults.get('access_gastos', False))
        
        # Test produccion
        produccion_defaults = RolePermission.get_default_permissions('produccion')
        self.assertTrue(produccion_defaults['access_dashboard'])
        self.assertTrue(produccion_defaults['access_produccion'])
        self.assertTrue(produccion_defaults['access_inventario'])
        self.assertFalse(produccion_defaults.get('access_contratos', False))
        
        # Test operario
        operario_defaults = RolePermission.get_default_permissions('operario')
        self.assertTrue(operario_defaults['access_dashboard'])
        self.assertTrue(operario_defaults['access_agenda'])
        self.assertFalse(operario_defaults.get('access_reportes', False))


class HU01RoleAPITest(APITestCase):
    """Tests de API para roles según HU01"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Studio",
            business_name="Test Business",
            business_address="Test Address",
            business_phone="123456789",
            business_email="test@test.com",
            business_ruc="12345678901"
        )
        
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="adminpass123",
            tenant=self.tenant,
            role="admin"
        )
        
        UserProfile.objects.create(user=self.admin_user)
        
        # Crear permisos por defecto para los nuevos roles
        RolePermission.objects.create(
            tenant=self.tenant,
            role="ventas",
            **RolePermission.get_default_permissions("ventas")
        )
        RolePermission.objects.create(
            tenant=self.tenant,
            role="produccion",
            **RolePermission.get_default_permissions("produccion")
        )
        
        # Autenticar
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_roles_list_api_returns_hu01_roles(self):
        """Test que la API de roles devuelve solo los roles de HU01"""
        url = reverse('core:configuration:roles_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        role_codes = [role['code'] for role in response.data]
        expected_roles = ['admin', 'ventas', 'produccion', 'operario']  # sin super_admin
        
        self.assertEqual(set(role_codes), set(expected_roles))
        self.assertNotIn('super_admin', role_codes)  # Filtrado correctamente
    
    def test_create_user_with_new_roles(self):
        """Test crear usuarios con los nuevos roles"""
        url = reverse('core:configuration:users_create')
        
        # Test crear usuario con rol ventas
        data = {
            'username': 'test_ventas',
            'email': 'ventas@test.com',
            'first_name': 'Test',
            'last_name': 'Ventas',
            'role': 'ventas',
            'password': 'test123',
            'confirm_password': 'test123'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'ventas')
        
        # Verificar que el usuario se creó correctamente
        user = User.objects.get(username='test_ventas')
        self.assertEqual(user.role, 'ventas')
    
    def test_create_user_with_old_role_fails(self):
        """Test que crear usuario con rol antiguo falla"""
        url = reverse('core:configuration:users_create')
        
        data = {
            'username': 'test_old',
            'email': 'old@test.com',
            'first_name': 'Test',
            'last_name': 'Old',
            'role': 'employee',  # Rol antiguo
            'password': 'test123',
            'confirm_password': 'test123'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)
    
    def test_role_permissions_api_works_with_new_roles(self):
        """Test que la API de permisos funciona con los nuevos roles"""
        # Test rol ventas
        url = reverse('core:configuration:permissions_view', kwargs={'role': 'ventas'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'ventas')
        self.assertEqual(response.data['role_display'], 'Ventas')
        
        # Test rol produccion
        url = reverse('core:configuration:permissions_view', kwargs={'role': 'produccion'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'produccion')
        self.assertEqual(response.data['role_display'], 'Producción')