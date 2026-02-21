"""
Tests del Módulo de Activos - Arte Ideas Operations
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import Activo, Financiamiento, Mantenimiento, Repuesto

User = get_user_model()


class ActivoModelTest(TestCase):
    """Tests para el modelo Activo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='admin'
        )
    
    def test_create_activo(self):
        """Test crear activo"""
        activo = Activo.objects.create(
            nombre='Impresora Canon',
            categoria='impresora',
            proveedor='Canon Perú',
            fecha_compra=date.today(),
            costo_total=Decimal('5000.00'),
            tipo_pago='contado',
            vida_util=60,  # 5 años
            depreciacion_mensual=Decimal('83.33'),
            estado='activo'
        )
        
        self.assertEqual(activo.nombre, 'Impresora Canon')
        self.assertEqual(activo.categoria, 'impresora')
        self.assertEqual(activo.estado, 'activo')
    
    def test_activo_str_method(self):
        """Test método string del activo"""
        activo = Activo.objects.create(
            nombre='Equipo Test',
            categoria='equipo de oficina',
            proveedor='Test Provider',
            fecha_compra=date.today(),
            costo_total=Decimal('1000.00'),
            tipo_pago='contado',
            vida_util=36,
            depreciacion_mensual=Decimal('27.78'),
            estado='activo'
        )
        
        self.assertEqual(str(activo), 'Equipo Test')


class FinanciamientoModelTest(TestCase):
    """Tests para el modelo Financiamiento"""
    
    def setUp(self):
        """Configuración inicial"""
        self.activo = Activo.objects.create(
            nombre='Activo Financiado',
            categoria='maquinaria',
            proveedor='Test Provider',
            fecha_compra=date.today(),
            costo_total=Decimal('10000.00'),
            tipo_pago='financiado',
            vida_util=60,
            depreciacion_mensual=Decimal('166.67'),
            estado='activo'
        )
    
    def test_create_financiamiento(self):
        """Test crear financiamiento"""
        financiamiento = Financiamiento.objects.create(
            activo=self.activo,
            tipo_pago='financiado',
            entidad_financiera='Banco Test',
            monto_financiado=Decimal('10000.00'),
            cuotas_totales=24,
            cuota_mensual=Decimal('500.00'),
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=730),  # ~24 meses
            estado='activo'
        )
        
        self.assertEqual(financiamiento.monto_financiado, Decimal('10000.00'))
        self.assertEqual(financiamiento.cuotas_totales, 24)
        self.assertEqual(financiamiento.estado, 'activo')


class MantenimientoModelTest(TestCase):
    """Tests para el modelo Mantenimiento"""
    
    def setUp(self):
        """Configuración inicial"""
        self.activo = Activo.objects.create(
            nombre='Activo para Mantenimiento',
            categoria='maquinaria',
            proveedor='Test Provider',
            fecha_compra=date.today(),
            costo_total=Decimal('5000.00'),
            tipo_pago='contado',
            vida_util=60,
            depreciacion_mensual=Decimal('83.33'),
            estado='activo'
        )
    
    def test_create_mantenimiento(self):
        """Test crear mantenimiento"""
        mantenimiento = Mantenimiento.objects.create(
            activo=self.activo,
            tipo_mantenimiento='preventivo',
            fecha_mantenimiento=date.today(),
            proveedor='Servicio Técnico Test',
            costo=Decimal('200.00'),
            proxima_fecha_mantenimiento=date.today() + timedelta(days=90),
            descripcion='Mantenimiento preventivo trimestral'
        )
        
        self.assertEqual(mantenimiento.tipo_mantenimiento, 'preventivo')
        self.assertEqual(mantenimiento.estado_del_mantenimiento, 'programado')
        self.assertEqual(mantenimiento.costo, Decimal('200.00'))


class RepuestoModelTest(TestCase):
    """Tests para el modelo Repuesto"""
    
    def test_create_repuesto(self):
        """Test crear repuesto"""
        repuesto = Repuesto.objects.create(
            nombre='Tinta Canon Negra',
            categoria='insumos impresoras',
            ubicacion='almacen A',
            proveedor='Canon Perú',
            codigo='CANON-BK-001',
            stock_actual=10,
            stock_minimo=3,
            costo_unitario=Decimal('45.00'),
            descripcion='Cartucho de tinta negra para impresora Canon'
        )
        
        self.assertEqual(repuesto.nombre, 'Tinta Canon Negra')
        self.assertEqual(repuesto.stock_actual, 10)
        self.assertEqual(repuesto.categoria, 'insumos impresoras')


class ActivosAPITest(TestCase):
    """Tests para la API de activos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.activo = Activo.objects.create(
            nombre='Activo API Test',
            categoria='impresora',
            proveedor='Test Provider',
            fecha_compra=date.today(),
            costo_total=Decimal('3000.00'),
            tipo_pago='contado',
            vida_util=36,
            depreciacion_mensual=Decimal('83.33'),
            estado='activo'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_activos(self):
        """Test dashboard de activos"""
        response = self.client.get('/operations/activos/api/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_activos', response.data)
        self.assertEqual(response.data['total_activos'], 1)
    
    def test_list_activos(self):
        """Test listar activos"""
        response = self.client.get('/operations/activos/api/activos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Activo API Test')
    
    def test_activos_por_categoria(self):
        """Test obtener activos por categoría"""
        response = self.client.get('/operations/activos/api/activos/por-categoria/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categorias', response.data)


class RepuestosAPITest(TestCase):
    """Tests para la API de repuestos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Repuesto con stock normal
        self.repuesto_normal = Repuesto.objects.create(
            nombre='Repuesto Normal',
            categoria='insumos impresoras',
            ubicacion='almacen A',
            proveedor='Test Provider',
            codigo='REP-001',
            stock_actual=20,
            stock_minimo=5,
            costo_unitario=Decimal('25.00')
        )
        
        # Repuesto con stock bajo
        self.repuesto_bajo = Repuesto.objects.create(
            nombre='Repuesto Bajo Stock',
            categoria='repuestos impresoras',
            ubicacion='almacen B',
            proveedor='Test Provider',
            codigo='REP-002',
            stock_actual=2,
            stock_minimo=5,
            costo_unitario=Decimal('50.00')
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_alertas_stock(self):
        """Test obtener repuestos con alertas de stock"""
        response = self.client.get('/operations/activos/api/repuestos/alertas-stock/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe aparecer el repuesto con stock bajo
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Repuesto Bajo Stock')
    
    def test_actualizar_stock(self):
        """Test actualizar stock de repuesto"""
        response = self.client.post(
            f'/operations/activos/api/repuestos/{self.repuesto_normal.id}/actualizar-stock/',
            {
                'cantidad': 5,
                'operacion': 'agregar',
                'motivo': 'Compra nueva'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stock_actual', response.data)
        
        # Verificar que el stock se actualizó
        self.repuesto_normal.refresh_from_db()
        self.assertEqual(self.repuesto_normal.stock_actual, 25)  # 20 + 5
