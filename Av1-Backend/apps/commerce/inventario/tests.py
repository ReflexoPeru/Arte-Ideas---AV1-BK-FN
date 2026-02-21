"""
Tests del Módulo de Inventario - Arte Ideas Commerce
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from apps.core.models import Tenant
from .models import (
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
)

User = get_user_model()


class BaseInventarioTest(TestCase):
    """Test base para modelos de inventario"""
    
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


class MolduraListonTest(BaseInventarioTest):
    """Tests para Moldura Listón"""
    
    def test_create_moldura_liston(self):
        """Test crear moldura listón"""
        moldura = MolduraListon.objects.create(
            tenant=self.tenant,
            nombre_producto='Moldura Clásica Dorada',
            stock_disponible=50,
            stock_minimo=10,
            costo_unitario=Decimal('15.50'),
            precio_venta=Decimal('25.00'),
            nombre_moldura='clasica',
            ancho='1',
            color='dorado',
            material='madera'
        )
        
        self.assertEqual(moldura.nombre_producto, 'Moldura Clásica Dorada')
        self.assertEqual(moldura.stock_disponible, 50)
        self.assertEqual(moldura.costo_total, Decimal('775.00'))  # 50 * 15.50
        self.assertFalse(moldura.alerta_stock)  # 50 > 10
    
    def test_alerta_stock(self):
        """Test alerta de stock"""
        moldura = MolduraListon.objects.create(
            tenant=self.tenant,
            nombre_producto='Moldura Bajo Stock',
            stock_disponible=5,
            stock_minimo=10,
            costo_unitario=Decimal('15.50'),
            precio_venta=Decimal('25.00'),
            nombre_moldura='clasica',
            ancho='1',
            color='dorado',
            material='madera'
        )
        
        self.assertTrue(moldura.alerta_stock)  # 5 <= 10


class MinilabTest(BaseInventarioTest):
    """Tests para Minilab"""
    
    def test_create_minilab_product(self):
        """Test crear producto de minilab"""
        minilab = Minilab.objects.create(
            tenant=self.tenant,
            nombre_producto='Papel Lustre 10x15',
            stock_disponible=100,
            stock_minimo=20,
            costo_unitario=Decimal('0.50'),
            precio_venta=Decimal('1.00'),
            tipo_insumo='papel',
            nombre_tipo='papel_lustre',
            tamaño_presentacion='10x15',
            fecha_compra='2024-01-15'
        )
        
        self.assertEqual(minilab.tipo_insumo, 'papel')
        self.assertEqual(minilab.nombre_tipo, 'papel_lustre')
        self.assertEqual(minilab.costo_total, Decimal('50.00'))  # 100 * 0.50


class CorteLaserTest(BaseInventarioTest):
    """Tests para Corte Láser"""
    
    def test_create_corte_laser_product(self):
        """Test crear producto de corte láser"""
        corte_laser = CorteLaser.objects.create(
            tenant=self.tenant,
            nombre_producto='Plancha MDF Jeans 60x70',
            stock_disponible=25,
            stock_minimo=5,
            costo_unitario=Decimal('45.00'),
            precio_venta=Decimal('75.00'),
            producto='plancha_mdf_jeans',
            tipo='mdf',
            tamaño='60x70',
            color='natural',
            unidad='plancha'
        )
        
        self.assertEqual(corte_laser.producto, 'plancha_mdf_jeans')
        self.assertEqual(corte_laser.tipo, 'mdf')
        self.assertEqual(corte_laser.costo_total, Decimal('1125.00'))  # 25 * 45.00


class InventarioAPITest(BaseInventarioTest):
    """Tests para la API de inventario"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear algunos productos de prueba
        self.moldura = MolduraListon.objects.create(
            tenant=self.tenant,
            nombre_producto='Moldura Test',
            stock_disponible=30,
            stock_minimo=10,
            costo_unitario=Decimal('20.00'),
            precio_venta=Decimal('35.00'),
            nombre_moldura='clasica',
            ancho='1',
            color='dorado',
            material='madera'
        )
        
        self.minilab = Minilab.objects.create(
            tenant=self.tenant,
            nombre_producto='Papel Test',
            stock_disponible=3,  # Bajo stock
            stock_minimo=10,
            costo_unitario=Decimal('0.75'),
            precio_venta=Decimal('1.50'),
            tipo_insumo='papel',
            nombre_tipo='papel_lustre',
            tamaño_presentacion='20x30',
            fecha_compra='2024-01-15'
        )
    
    def test_dashboard_inventario(self):
        """Test dashboard de inventario"""
        response = self.client.get('/commerce/inventario/api/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_productos', response.data)
        self.assertIn('alertas_stock', response.data)
        self.assertEqual(response.data['total_productos'], 2)
        self.assertEqual(response.data['alertas_stock'], 1)  # Solo minilab tiene alerta
    
    def test_metricas_inventario(self):
        """Test métricas de inventario"""
        response = self.client.get('/commerce/inventario/api/metricas/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_productos', response.data)
        self.assertIn('valor_total_inventario', response.data)
        self.assertIn('categorias', response.data)
    
    def test_list_moldura_liston(self):
        """Test listar molduras listón"""
        response = self.client.get('/commerce/inventario/api/moldura-liston/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre_producto'], 'Moldura Test')
    
    def test_alertas_stock_moldura(self):
        """Test alertas de stock para molduras"""
        response = self.client.get('/commerce/inventario/api/moldura-liston/alertas-stock/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La moldura no debería aparecer en alertas (30 > 10)
        self.assertEqual(len(response.data), 0)
    
    def test_alertas_stock_minilab(self):
        """Test alertas de stock para minilab"""
        response = self.client.get('/commerce/inventario/api/minilab/alertas-stock/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El minilab debería aparecer en alertas (3 <= 10)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_producto'], 'Papel Test')


class InventarioValidationTest(BaseInventarioTest):
    """Tests para validaciones de inventario"""
    
    def test_stock_negativo_validation(self):
        """Test validación de stock negativo"""
        with self.assertRaises(Exception):
            MolduraListon.objects.create(
                tenant=self.tenant,
                nombre_producto='Moldura Inválida',
                stock_disponible=-5,  # Stock negativo
                stock_minimo=10,
                costo_unitario=Decimal('20.00'),
                precio_venta=Decimal('35.00'),
                nombre_moldura='clasica',
                ancho='1',
                color='dorado',
                material='madera'
            )
    
    def test_costo_unitario_validation(self):
        """Test validación de costo unitario"""
        with self.assertRaises(Exception):
            MolduraListon.objects.create(
                tenant=self.tenant,
                nombre_producto='Moldura Inválida',
                stock_disponible=10,
                stock_minimo=5,
                costo_unitario=Decimal('0.00'),  # Costo inválido
                precio_venta=Decimal('35.00'),
                nombre_moldura='clasica',
                ancho='1',
                color='dorado',
                material='madera'
            )