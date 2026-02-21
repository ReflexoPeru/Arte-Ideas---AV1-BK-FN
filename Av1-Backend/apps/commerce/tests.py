"""
Tests de Integración del Commerce App - Arte Ideas
Tests principales para integración entre módulos
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.core.models import Tenant
from apps.crm.models import Cliente

# Importar desde módulos específicos
from .pedidos.models import Order
from .inventario.models import MolduraListon

User = get_user_model()


class CommerceIntegrationTest(TestCase):
    """Tests de integración entre módulos de Commerce"""
    
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
    
    def test_modules_integration(self):
        """Test integración entre módulos de pedidos e inventario"""
        # Crear producto de inventario
        from decimal import Decimal
        moldura = MolduraListon.objects.create(
            tenant=self.tenant,
            nombre_producto='Moldura Test',
            stock_disponible=10,
            stock_minimo=5,
            costo_unitario=Decimal('20.00'),
            precio_venta=Decimal('35.00'),
            nombre_moldura='clasica',
            ancho='1',
            color='dorado',
            material='madera'
        )
        
        # Crear pedido que use el producto
        from django.utils import timezone
        from datetime import timedelta
        
        order = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-INT-001',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timedelta(days=7),
            total=70.00,  # 2 * 35.00
            status='pendiente'
        )
        
        # Verificar que ambos módulos funcionan correctamente
        self.assertEqual(order.cliente.obtener_nombre_completo(), 'Juan Pérez')
        self.assertEqual(moldura.costo_total, Decimal('200.00'))  # 10 * 20.00
        self.assertFalse(moldura.alerta_stock)  # 10 > 5
    
    def test_api_endpoints_integration(self):
        """Test integración de endpoints de API"""
        # Test endpoint de pedidos
        response = self.client.get('/commerce/pedidos/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test endpoint de inventario
        response = self.client.get('/commerce/inventario/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test endpoints de compatibilidad
        response = self.client.get('/commerce/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/commerce/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)