"""
Tests del Módulo de Autenticación - Arte Ideas
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.core.multitenancy.models import Tenant

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    """Tests para autenticación de usuarios"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.tenant = Tenant.objects.create(
            name="Estudio Test",
            slug="estudio-test",
            business_name="Estudio Fotográfico Test",
            business_address="Dirección Test",
            business_phone="123456789",
            business_email="test@estudio.com",
            business_ruc="12345678901"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            tenant=self.tenant,
            role="admin"
        )
    
    def test_user_creation(self):
        """Test de creación de usuario"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.tenant, self.tenant)
        self.assertEqual(self.user.role, "admin")
    
    def test_user_permissions(self):
        """Test de permisos de usuario"""
        permissions = self.user.get_permissions_list()
        self.assertIn('access:dashboard', permissions)
        self.assertIn('manage:users', permissions)
        
        # Test has_permission method
        self.assertTrue(self.user.has_permission('access:dashboard'))
        self.assertFalse(self.user.has_permission('invalid:permission'))