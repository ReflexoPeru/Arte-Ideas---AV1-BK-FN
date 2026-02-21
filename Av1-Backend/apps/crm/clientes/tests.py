"""
Tests del Módulo de Clientes - Arte Ideas CRM
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.core.models import Tenant
from .models import Cliente, HistorialCliente, ContactoCliente

User = get_user_model()


class ClienteModelTestCase(TestCase):
    """Tests para el modelo Cliente"""
    
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
    
    def test_cliente_particular_creation(self):
        """Test de creación de cliente particular"""
        cliente = Cliente.objects.create(
            tenant=self.tenant,
            tipo_cliente='particular',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@example.com',
            telefono='987654321',
            dni='12345678',
            direccion='Av. Test 123'
        )
        
        self.assertEqual(cliente.tipo_cliente, 'particular')
        self.assertEqual(cliente.obtener_nombre_completo(), 'Juan Pérez')
        self.assertTrue(cliente.activo)
    
    def test_cliente_empresa_creation(self):
        """Test de creación de cliente empresa"""
        cliente = Cliente.objects.create(
            tenant=self.tenant,
            tipo_cliente='empresa',
            nombres='María',
            apellidos='García',
            email='maria@empresa.com',
            telefono='987654321',
            dni='20123456789',
            direccion='Jr. Empresa 456',
            razon_social='Empresa Test SAC'
        )
        
        self.assertEqual(cliente.tipo_cliente, 'empresa')
        self.assertEqual(cliente.razon_social, 'Empresa Test SAC')
        self.assertIn('Empresa Test SAC', str(cliente))
    
    def test_cliente_colegio_creation(self):
        """Test de creación de cliente colegio"""
        cliente = Cliente.objects.create(
            tenant=self.tenant,
            tipo_cliente='colegio',
            nombres='Ana',
            apellidos='López',
            email='ana@colegio.edu.pe',
            telefono='987654321',
            dni='20987654321',
            direccion='Av. Educación 789',
            nivel_educativo='primaria',
            grado='5to',
            seccion='A'
        )
        
        self.assertEqual(cliente.tipo_cliente, 'colegio')
        self.assertEqual(cliente.nivel_educativo, 'primaria')
        self.assertEqual(cliente.grado, '5to')
        self.assertEqual(cliente.seccion, 'A')


class HistorialClienteTestCase(TestCase):
    """Tests para el modelo HistorialCliente"""
    
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
        
        self.cliente = Cliente.objects.create(
            tenant=self.tenant,
            tipo_cliente='particular',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@example.com',
            telefono='987654321',
            dni='12345678',
            direccion='Av. Test 123'
        )
    
    def test_historial_creation(self):
        """Test de creación de historial"""
        from django.utils import timezone
        
        historial = HistorialCliente.objects.create(
            cliente=self.cliente,
            tipo_interaccion='llamada',
            fecha=timezone.now(),
            descripcion='Llamada para consultar precios',
            resultado='Interesado en paquete básico',
            registrado_por=self.user
        )
        
        self.assertEqual(historial.cliente, self.cliente)
        self.assertEqual(historial.tipo_interaccion, 'llamada')
        self.assertEqual(historial.registrado_por, self.user)


class ContactoClienteTestCase(TestCase):
    """Tests para el modelo ContactoCliente"""
    
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
        
        self.cliente = Cliente.objects.create(
            tenant=self.tenant,
            tipo_cliente='empresa',
            nombres='María',
            apellidos='García',
            email='maria@empresa.com',
            telefono='987654321',
            dni='20123456789',
            direccion='Jr. Empresa 456',
            razon_social='Empresa Test SAC'
        )
    
    def test_contacto_creation(self):
        """Test de creación de contacto"""
        contacto = ContactoCliente.objects.create(
            cliente=self.cliente,
            nombre='Carlos Rodríguez',
            cargo='Gerente de Marketing',
            telefono='999888777',
            email='carlos@empresa.com',
            es_principal=True
        )
        
        self.assertEqual(contacto.cliente, self.cliente)
        self.assertEqual(contacto.nombre, 'Carlos Rodríguez')
        self.assertTrue(contacto.es_principal)


class ClienteAPITestCase(APITestCase):
    """Tests para la API de clientes"""
    
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
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_cliente_particular(self):
        """Test de creación de cliente particular via API"""
        data = {
            'tipo_cliente': 'particular',
            'nombres': 'Juan',
            'apellidos': 'Pérez',
            'email': 'juan@example.com',
            'telefono': '987654321',
            'dni': '12345678',
            'direccion': 'Av. Test 123'
        }
        
        response = self.client.post('/api/crm/clientes/clientes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.count(), 1)
        
        cliente = Cliente.objects.first()
        self.assertEqual(cliente.tenant, self.tenant)
        self.assertEqual(cliente.nombres, 'Juan')
    
    def test_list_clientes(self):
        """Test de listado de clientes via API"""
        Cliente.objects.create(
            tenant=self.tenant,
            tipo_cliente='particular',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@example.com',
            telefono='987654321',
            dni='12345678',
            direccion='Av. Test 123'
        )
        
        response = self.client.get('/api/crm/clientes/clientes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)