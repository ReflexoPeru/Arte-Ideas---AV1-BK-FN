"""
Tests del Módulo de Configuración del Sistema - Arte Ideas
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.core.multitenancy.models import Tenant
from .models import SystemConfiguration

User = get_user_model()


class SystemConfigurationTestCase(TestCase):
    """Tests para configuraciones del sistema"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.config = SystemConfiguration.objects.create(
            key="test_setting",
            value="test_value",
            description="Configuración de prueba"
        )
    
    def test_system_configuration_creation(self):
        """Test de creación de configuración del sistema"""
        self.assertEqual(self.config.key, "test_setting")
        self.assertEqual(self.config.value, "test_value")
        self.assertTrue(self.config.is_active)
    
    def test_system_configuration_str(self):
        """Test del método __str__ de configuración"""
        expected = "test_setting: test_value"
        self.assertEqual(str(self.config), expected)