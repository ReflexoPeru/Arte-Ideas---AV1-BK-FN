"""
Modelos del Commerce App - Arte Ideas
Importaciones centralizadas para compatibilidad con migraciones
"""

# Importar modelos de pedidos
from .pedidos.models import Order, OrderItem, OrderPayment, OrderStatusHistory

# Importar modelos de inventario
from .inventario.models import (
    BaseInventarioModel,
    # Enmarcados
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    # Minilab
    Minilab,
    # Graduaciones
    Cuadro, Anuario,
    # Corte Láser
    CorteLaser,
    # Accesorios
    MarcoAccesorio, HerramientaGeneral
)

# Mantener Product para compatibilidad con código legacy
from django.db import models
from apps.core.models import Tenant


class Product(models.Model):
    """
    Modelo básico de productos/servicios para compatibilidad con código legacy
    NOTA: Para nuevos desarrollos, usar los modelos específicos del módulo inventario
    """
    PRODUCT_TYPE_CHOICES = [
        ('product', 'Producto'),
        ('service', 'Servicio'),
    ]
    
    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Estudio Fotográfico')
    
    # Información básica
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='product',
        verbose_name='Tipo'
    )
    
    # Precios
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Unitario')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Precio de Costo')
    
    # Inventario
    stock_quantity = models.IntegerField(default=0, verbose_name='Stock Disponible')
    min_stock = models.IntegerField(default=0, verbose_name='Stock Mínimo')
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto/Servicio (Legacy)'
        verbose_name_plural = 'Productos/Servicios (Legacy)'
        ordering = ['name']
        unique_together = ['tenant', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_product_type_display()})"
    
    def is_in_stock(self):
        """Verificar si hay stock disponible"""
        return self.stock_quantity > 0
    
    def needs_restock(self):
        """Verificar si necesita reabastecimiento"""
        return self.stock_quantity <= self.min_stock