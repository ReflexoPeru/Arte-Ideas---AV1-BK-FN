"""
Tests de Integración del Operations App - Arte Ideas
Tests principales para integración entre módulos
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from apps.core.models import Tenant
from apps.crm.models import Cliente
from apps.commerce.models import Order

# Importar desde módulos específicos
from .produccion.models import OrdenProduccion
from .activos.models import Activo, Repuesto

User = get_user_model()


class OperationsIntegrationTest(TestCase):
    """Tests de integración entre módulos de Operations"""
    
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
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_modules_integration(self):
        """Test integración entre módulos de producción y activos"""
        # Crear activo para producción
        activo = Activo.objects.create(
            nombre='Impresora Producción',
            categoria='impresora',
            proveedor='Canon',
            fecha_compra=date.today(),
            costo_total=Decimal('5000.00'),
            tipo_pago='contado',
            vida_util=60,
            depreciacion_mensual=Decimal('83.33'),
            estado='activo'
        )
        
        # Crear pedido
        pedido = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-INT-001',
            cliente=self.cliente,
            document_type='proforma',
            client_type='particular',
            start_date=date.today(),
            delivery_date=date.today() + timedelta(days=7),
            total=150.00,
            status='pendiente'
        )
        
        # Crear orden de producción
        orden = OrdenProduccion.objects.create(
            numero_op='OP-INT-001',
            pedido=pedido,
            descripcion='Impresión con activo específico',
            tipo='Minilab',
            operario=self.operario,
            fecha_estimada=date.today() + timedelta(days=3),
            id_inquilino=self.tenant
        )
        
        # Crear repuesto relacionado
        repuesto = Repuesto.objects.create(
            nombre='Tinta para Impresora',
            categoria='insumos impresoras',
            ubicacion='almacen A',
            proveedor='Canon',
            codigo='TINTA-001',
            stock_actual=10,
            stock_minimo=3,
            costo_unitario=Decimal('45.00')
        )
        
        # Verificar que ambos módulos funcionan correctamente
        self.assertEqual(orden.cliente.obtener_nombre_completo(), 'Juan Pérez')
        self.assertEqual(activo.estado, 'activo')
        self.assertEqual(repuesto.stock_actual, 10)
    
    def test_api_endpoints_integration(self):
        """Test integración de endpoints de API"""
        # Test endpoint de producción
        response = self.client.get('/operations/produccion/api/ordenes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test endpoint de activos
        response = self.client.get('/operations/activos/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test endpoints de compatibilidad
        response = self.client.get('/operations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_workflow_produccion_activos(self):
        """Test flujo de trabajo entre producción y activos"""
        # 1. Crear activo necesario para producción
        activo = Activo.objects.create(
            nombre='Máquina Corte Láser',
            categoria='maquinaria',
            proveedor='Laser Tech',
            fecha_compra=date.today(),
            costo_total=Decimal('15000.00'),
            tipo_pago='financiado',
            vida_util=120,
            depreciacion_mensual=Decimal('125.00'),
            estado='activo'
        )
        
        # 2. Crear repuestos necesarios
        repuesto = Repuesto.objects.create(
            nombre='Lente de Enfoque Láser',
            categoria='repuestos camaras',
            ubicacion='almacen A',
            proveedor='Laser Tech',
            codigo='LENS-001',
            stock_actual=2,
            stock_minimo=1,
            costo_unitario=Decimal('200.00')
        )
        
        # 3. Crear pedido que requiere corte láser
        pedido = Order.objects.create(
            tenant=self.tenant,
            order_number='ORD-LASER-001',
            cliente=self.cliente,
            document_type='nota_venta',
            client_type='particular',
            start_date=date.today(),
            delivery_date=date.today() + timedelta(days=5),
            total=300.00,
            status='pendiente'
        )
        
        # 4. Crear orden de producción
        orden = OrdenProduccion.objects.create(
            numero_op='OP-LASER-001',
            pedido=pedido,
            descripcion='Corte láser personalizado',
            tipo='Corte Láser',
            operario=self.operario,
            fecha_estimada=date.today() + timedelta(days=2),
            id_inquilino=self.tenant
        )
        
        # 5. Verificar que el flujo está completo
        self.assertEqual(activo.estado, 'activo')
        self.assertEqual(orden.tipo, 'Corte Láser')
        self.assertEqual(repuesto.stock_actual, 2)
        
        # 6. Simular uso de repuesto en producción
        repuesto.stock_actual -= 1
        repuesto.save()
        
        # 7. Verificar alerta de stock
        self.assertEqual(repuesto.stock_actual, 1)
        self.assertEqual(repuesto.stock_actual, repuesto.stock_minimo)