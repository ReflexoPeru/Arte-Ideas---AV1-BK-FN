"""
Tests del Módulo de Pedidos - Arte Ideas Commerce
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from apps.core.models import Tenant
from apps.crm.models import Cliente
from .models import Order, OrderItem, OrderPayment, OrderStatusHistory

User = get_user_model()


class OrderModelTest(TestCase):
    """Tests para el modelo Order"""
    
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
    
    def test_create_order(self):
        """Test crear pedido"""
        order = Order.objects.create(
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
        
        self.assertEqual(order.order_number, 'ORD-001')
        self.assertEqual(order.status, 'pendiente')
        self.assertEqual(order.balance, 150.00)
    
    def test_order_balance_calculation(self):
        """Test cálculo automático del balance"""
        order = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-002',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=200.00,
            paid_amount=50.00,
            status='pendiente'
        )
        
        self.assertEqual(order.balance, 150.00)
    
    def test_order_status_history(self):
        """Test historial de estados"""
        order = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-003',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=100.00,
            status='pendiente'
        )
        
        # Cambiar estado
        OrderStatusHistory.objects.create(
            order=order,
            previous_status='pendiente',
            new_status='confirmado',
            reason='Confirmado por cliente',
            changed_by=self.user
        )
        
        order.status = 'confirmado'
        order.save()
        
        self.assertEqual(order.status, 'confirmado')
        self.assertEqual(order.status_history.count(), 1)


class OrderPaymentTest(TestCase):
    """Tests para pagos de pedidos"""
    
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
        
        self.order = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-PAY-001',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=500.00,
            status='pendiente'
        )
    
    def test_create_payment(self):
        """Test crear pago"""
        payment = OrderPayment.objects.create(
            order=self.order,
            payment_date=timezone.now().date(),
            amount=200.00,
            payment_method='efectivo',
            registered_by=self.user
        )
        
        self.assertEqual(payment.amount, 200.00)
        self.assertEqual(payment.payment_method, 'efectivo')
        
        # Verificar que se actualizó el pedido
        self.order.refresh_from_db()
        self.assertEqual(self.order.paid_amount, 200.00)
        self.assertEqual(self.order.balance, 300.00)


class OrderAPITest(TestCase):
    """Tests para la API de pedidos"""
    
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
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_orders(self):
        """Test listar pedidos"""
        Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-API-001',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=150.00,
            status='pendiente'
        )
        
        response = self.client.get('/commerce/pedidos/api/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_order_statistics(self):
        """Test estadísticas de pedidos"""
        Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-STAT-001',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=300.00,
            paid_amount=100.00,
            status='pendiente'
        )
        
        response = self.client.get('/commerce/pedidos/api/orders/estadisticas/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totals', response.data)
        self.assertEqual(response.data['totals']['total_orders'], 1)
        self.assertEqual(float(response.data['totals']['total_amount']), 300.00)