"""
Tests del Módulo de Multi-tenancy - Arte Ideas
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Tenant, TenantConfiguration

User = get_user_model()


class TenantTestCase(TestCase):
    """Tests para modelo Tenant"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.tenant = Tenant.objects.create(
            name="Estudio Test",
            business_name="Estudio Fotográfico Test",
            business_address="Dirección Test",
            business_phone="123456789",
            business_email="test@estudio.com",
            business_ruc="12345678901"
        )
    
    def test_tenant_creation(self):
        """Test de creación de tenant"""
        self.assertEqual(self.tenant.name, "Estudio Test")
        self.assertEqual(self.tenant.business_name, "Estudio Fotográfico Test")
        self.assertTrue(self.tenant.is_active)
        self.assertIsNotNone(self.tenant.slug)  # Se genera automáticamente
    
    def test_tenant_slug_generation(self):
        """Test de generación automática de slug"""
        # El slug se genera automáticamente en el método save()
        self.assertTrue(len(self.tenant.slug) > 0)
    
    def test_tenant_access_methods(self):
        """Test de métodos de acceso del tenant"""
        # Por defecto location_type es 'lima'
        self.assertTrue(self.tenant.has_global_data_access())
        self.assertTrue(self.tenant.has_financial_modules())
        
        # Cambiar a provincia
        self.tenant.location_type = 'provincia'
        self.tenant.save()
        
        self.assertFalse(self.tenant.has_global_data_access())
        self.assertFalse(self.tenant.has_financial_modules())


class TenantConfigurationTestCase(TestCase):
    """Tests para configuraciones específicas de tenant"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.tenant = Tenant.objects.create(
            name="Estudio Test",
            business_name="Estudio Fotográfico Test",
            business_address="Dirección Test",
            business_phone="123456789",
            business_email="test@estudio.com",
            business_ruc="12345678901"
        )
        
        self.config = TenantConfiguration.objects.create(
            tenant=self.tenant,
            module='general',
            key='test_setting',
            value='test_value',
            data_type='string'
        )
    
    def test_tenant_configuration_creation(self):
        """Test de creación de configuración de tenant"""
        self.assertEqual(self.config.tenant, self.tenant)
        self.assertEqual(self.config.module, 'general')
        self.assertEqual(self.config.key, 'test_setting')
        self.assertEqual(self.config.value, 'test_value')
    
    def test_get_typed_value(self):
        """Test de obtención de valor con tipo correcto"""
        # String
        self.assertEqual(self.config.get_typed_value(), 'test_value')
        
        # Integer
        int_config = TenantConfiguration.objects.create(
            tenant=self.tenant,
            module='general',
            key='int_setting',
            value='42',
            data_type='integer'
        )
        self.assertEqual(int_config.get_typed_value(), 42)
        
        # Boolean
        bool_config = TenantConfiguration.objects.create(
            tenant=self.tenant,
            module='general',
            key='bool_setting',
            value='true',
            data_type='boolean'
        )
        self.assertTrue(bool_config.get_typed_value())