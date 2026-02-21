"""
Tests del Módulo de Producción - Arte Ideas Operations
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from apps.core.models import Tenant
from apps.crm.models import Cliente
from apps.commerce.models import Order
from .models import OrdenProduccion

User = get_user_model()


class OrdenProduccionModelTest(TestCase):
    """Tests para el modelo OrdenProduccion"""
    
    def setUp(self):
        """Configuración inicial"""
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test',
            business_name='Test Business',
            business_address='Test Address',
            business_phone='123456789',
            business_email='test@test.com',
            business_ruc='12345678901'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            tenant=self.tenant,
            role='admin'
        )
        
        self.operario = User.objects.create_user(
            username='operario1',
            email='operario@test.com',
            password='testpass123',
            tenant=self.tenant,
            role='operario'
        )
        
        self.cliente = Cliente.objects.create(
            tenant=self.tenant,
            nombres='Juan',
            apellidos='Pérez',
            email='juan@test.com',
            telefono='987654321',
            dni='12345678',
            direccion='Test Address',
            tipo_cliente='particular'
        )
        
        self.pedido = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-001',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=150.00,
            status='pendiente'
        )
    
    def test_create_orden_produccion(self):
        """Test crear orden de producción"""
        orden = OrdenProduccion.objects.create(
            numero_op='OP-001',
            pedido=self.pedido,
            descripcion='Enmarcado de foto 20x30',
            tipo='Enmarcado',
            operario=self.operario,
            fecha_estimada=timezone.now().date() + timedelta(days=3),
            id_inquilino=self.tenant
        )
        
        self.assertEqual(orden.numero_op, 'OP-001')
        self.assertEqual(orden.estado, 'Pendiente')
        self.assertEqual(orden.cliente, self.cliente)  # Auto-asignado desde pedido
    
    def test_auto_assign_cliente(self):
        """Test auto-asignación de cliente desde pedido"""
        orden = OrdenProduccion.objects.create(
            numero_op='OP-002',
            pedido=self.pedido,
            descripcion='Test',
            tipo='Minilab',
            operario=self.operario,
            fecha_estimada=timezone.now().date() + timedelta(days=3),
            id_inquilino=self.tenant
        )
        
        # El cliente debe asignarse automáticamente desde el pedido
        self.assertEqual(orden.cliente, self.pedido.cliente)


class OrdenProduccionAPITest(TestCase):
    """Tests para la API de órdenes de producción"""
    
    def setUp(self):
        """Configuración inicial"""
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test',
            business_name='Test Business',
            business_address='Test Address',
            business_phone='123456789',
            business_email='test@test.com',
            business_ruc='12345678901'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            tenant=self.tenant,
            role='admin'
        )
        
        self.operario = User.objects.create_user(
            username='operario1',
            email='operario@test.com',
            password='testpass123',
            tenant=self.tenant,
            role='operario'
        )
        
        self.cliente = Cliente.objects.create(
            tenant=self.tenant,
            nombres='Juan',
            apellidos='Pérez',
            email='juan@test.com',
            telefono='987654321',
            dni='12345678',
            direccion='Test Address',
            tipo_cliente='particular'
        )
        
        self.pedido = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-001',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=150.00,
            status='pendiente'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_ordenes_produccion(self):
        """Test listar órdenes de producción"""
        OrdenProduccion.objects.create(
            numero_op='OP-API-001',
            pedido=self.pedido,
            descripcion='Test API',
            tipo='Enmarcado',
            operario=self.operario,
            fecha_estimada=timezone.now().date() + timedelta(days=3),
            id_inquilino=self.tenant
        )
        
        response = self.client.get('/operations/produccion/api/ordenes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_dashboard_estadisticas(self):
        """Test dashboard de estadísticas"""
        # Crear órdenes con diferentes estados
        OrdenProduccion.objects.create(
            numero_op='OP-PEND-001',
            pedido=self.pedido,
            descripcion='Pendiente',
            tipo='Enmarcado',
            estado='Pendiente',
            operario=self.operario,
            fecha_estimada=timezone.now().date() + timedelta(days=3),
            id_inquilino=self.tenant
        )
        
        response = self.client.get('/operations/produccion/api/ordenes/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pendientes', response.data)
        self.assertEqual(response.data['pendientes'], 1)
        self.assertEqual(response.data['total'], 1)