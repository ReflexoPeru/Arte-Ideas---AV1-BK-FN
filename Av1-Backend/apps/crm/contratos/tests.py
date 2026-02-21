"""
Tests del Módulo de Contratos - Arte Ideas CRM
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from apps.core.models import Tenant
from apps.crm.clientes.models import Cliente
from .models import Contrato, ClausulaContrato, PagoContrato, EstadoContrato

User = get_user_model()


class ContratoModelTestCase(TestCase):
    """Tests para el modelo Contrato"""
    
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
            tipo_cliente='particular',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@example.com',
            telefono='987654321',
            dni='12345678',
            direccion='Av. Test 123'
        )
    
    def test_contrato_creation(self):
        """Test de creación de contrato"""
        contrato = Contrato.objects.create(
            tenant=self.tenant,
            cliente=self.cliente,
            numero_contrato='CT-001',
            titulo='Sesión Fotográfica Familiar',
            descripcion='Sesión fotográfica para familia de 4 personas',
            tipo_servicio='fotografia',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            monto_total=Decimal('500.00'),
            adelanto=Decimal('200.00')
        )
        
        self.assertEqual(contrato.numero_contrato, 'CT-001')
        self.assertEqual(contrato.saldo_pendiente, Decimal('300.00'))
        self.assertEqual(contrato.porcentaje_adelanto, 40.0)
        self.assertEqual(contrato.estado, 'borrador')
    
    def test_contrato_validation(self):
        """Test de validaciones del contrato"""
        from django.core.exceptions import ValidationError
        
        # Test fecha fin menor a fecha inicio
        contrato = Contrato(
            tenant=self.tenant,
            cliente=self.cliente,
            numero_contrato='CT-002',
            titulo='Test',
            descripcion='Test',
            tipo_servicio='fotografia',
            fecha_inicio=date.today(),
            fecha_fin=date.today() - timedelta(days=1),  # Fecha inválida
            monto_total=Decimal('500.00')
        )
        
        with self.assertRaises(ValidationError):
            contrato.full_clean()
    
    def test_contrato_vencido(self):
        """Test de propiedad esta_vencido"""
        contrato = Contrato.objects.create(
            tenant=self.tenant,
            cliente=self.cliente,
            numero_contrato='CT-003',
            titulo='Contrato Vencido',
            descripcion='Test',
            tipo_servicio='fotografia',
            fecha_inicio=date.today() - timedelta(days=60),
            fecha_fin=date.today() - timedelta(days=1),  # Vencido ayer
            monto_total=Decimal('500.00'),
            estado='activo'
        )
        
        self.assertTrue(contrato.esta_vencido)


class ClausulaContratoTestCase(TestCase):
    """Tests para el modelo ClausulaContrato"""
    
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
            tipo_cliente='particular',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@example.com',
            telefono='987654321',
            dni='12345678',
            direccion='Av. Test 123'
        )
        
        self.contrato = Contrato.objects.create(
            tenant=self.tenant,
            cliente=self.cliente,
            numero_contrato='CT-001',
            titulo='Test',
            descripcion='Test',
            tipo_servicio='fotografia',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            monto_total=Decimal('500.00')
        )
    
    def test_clausula_creation(self):
        """Test de creación de cláusula"""
        clausula = ClausulaContrato.objects.create(
            contrato=self.contrato,
            numero_clausula=1,
            titulo='Entrega de Fotos',
            contenido='Las fotos serán entregadas en un plazo máximo de 15 días.'
        )
        
        self.assertEqual(clausula.contrato, self.contrato)
        self.assertEqual(clausula.numero_clausula, 1)
        self.assertEqual(str(clausula), 'Cláusula 1: Entrega de Fotos')


class PagoContratoTestCase(TestCase):
    """Tests para el modelo PagoContrato"""
    
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
        
        self.contrato = Contrato.objects.create(
            tenant=self.tenant,
            cliente=self.cliente,
            numero_contrato='CT-001',
            titulo='Test',
            descripcion='Test',
            tipo_servicio='fotografia',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            monto_total=Decimal('500.00')
        )
    
    def test_pago_creation(self):
        """Test de creación de pago"""
        pago = PagoContrato.objects.create(
            contrato=self.contrato,
            fecha_pago=date.today(),
            monto=Decimal('200.00'),
            metodo_pago='efectivo',
            registrado_por=self.user
        )
        
        self.assertEqual(pago.contrato, self.contrato)
        self.assertEqual(pago.monto, Decimal('200.00'))
        self.assertEqual(pago.registrado_por, self.user)


class ContratoAPITestCase(APITestCase):
    """Tests para la API de contratos"""
    
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
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_contrato(self):
        """Test de creación de contrato via API"""
        data = {
            'cliente': self.cliente.id,
            'numero_contrato': 'CT-001',
            'titulo': 'Sesión Fotográfica Familiar',
            'descripcion': 'Sesión fotográfica para familia',
            'tipo_servicio': 'fotografia',
            'fecha_inicio': date.today().isoformat(),
            'fecha_fin': (date.today() + timedelta(days=30)).isoformat(),
            'monto_total': '500.00',
            'adelanto': '200.00'
        }
        
        response = self.client.post('/api/crm/contratos/contratos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contrato.objects.count(), 1)
        
        contrato = Contrato.objects.first()
        self.assertEqual(contrato.tenant, self.tenant)
        self.assertEqual(contrato.numero_contrato, 'CT-001')
    
    def test_list_contratos(self):
        """Test de listado de contratos via API"""
        Contrato.objects.create(
            tenant=self.tenant,
            cliente=self.cliente,
            numero_contrato='CT-001',
            titulo='Test',
            descripcion='Test',
            tipo_servicio='fotografia',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            monto_total=Decimal('500.00')
        )
        
        response = self.client.get('/api/crm/contratos/contratos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)