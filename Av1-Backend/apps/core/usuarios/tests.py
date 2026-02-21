"""
Tests del Módulo de Usuarios - Arte Ideas
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.core.multitenancy.models import Tenant
from .models import UserProfile, UserActivity

User = get_user_model()


class UserProfileTestCase(TestCase):
    """Tests para perfiles de usuario"""
    
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
            tenant=self.tenant
        )
    
    def test_user_profile_creation(self):
        """Test de creación de perfil de usuario"""
        profile = UserProfile.objects.create(
            user=self.user,
            language='es',
            theme='light'
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.language, 'es')
        self.assertEqual(profile.theme, 'light')
    
    def test_user_activity_creation(self):
        """Test de creación de actividad de usuario"""
        activity = UserActivity.objects.create(
            user=self.user,
            tenant=self.tenant,
            action='login',
            description='Usuario inició sesión',
            module='auth'
        )
        
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.tenant, self.tenant)
        self.assertEqual(activity.action, 'login')