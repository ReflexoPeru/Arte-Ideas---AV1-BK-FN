"""
Administración del Commerce App - Arte Ideas
Importaciones centralizadas para compatibilidad

NOTA: Los admins específicos están organizados en:
- pedidos/admin.py - Órdenes, items, pagos e historial
- inventario/admin.py - Productos de inventario

Los modelos ya están registrados en sus respectivos módulos admin.
"""

# Importar administraciones de pedidos (ya registradas automáticamente)
from .pedidos import admin as pedidos_admin

# Importar administraciones de inventario (ya registradas automáticamente)  
from .inventario import admin as inventario_admin

# Los modelos ya están registrados en sus módulos específicos
# No necesitamos registrarlos aquí nuevamente
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.db.models import Sum, F, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Product
from .pedidos.models import Order, OrderItem

# Los alias están comentados porque los admins ya están registrados en sus módulos
# OrderAdmin = PedidosOrderAdmin
# OrderItemAdmin = PedidosOrderItemAdmin


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administración de Productos"""
    
    list_display = [
        'name', 'product_type', 'unit_price', 'stock_quantity', 'is_active',
        'low_stock_indicator', 'created_at_formatted'
    ]
    list_filter = [
        'product_type', 'is_active', 'created_at', 'updated_at'
    ]
    search_fields = [
        'name', 'description', 'sku'
    ]
    list_editable = ['unit_price', 'stock_quantity', 'is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'product_type', 'sku')
        }),
        ('Precio y Stock', {
            'fields': ('unit_price', 'stock_quantity', 'is_active')
        }),
        ('Imágenes', {
            'fields': ('image', 'image_preview')
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['image_preview', 'created_at_formatted', 'updated_at_formatted']
    
    def low_stock_indicator(self, obj):
        """Indicador visual de stock bajo"""
        if obj.stock_quantity <= 5:
            return mark_safe('<span style="color: red; font-weight: bold;">⚠️ Stock Bajo</span>')
        elif obj.stock_quantity <= 10:
            return mark_safe('<span style="color: orange;">⚡ Stock Medio</span>')
        else:
            return mark_safe('<span style="color: green;">✅ Stock Alto</span>')
    
    low_stock_indicator.short_description = 'Estado Stock'
    
    def image_preview(self, obj):
        """Vista previa de imagen del producto"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="150" style="object-fit: cover;" />')
        return mark_safe('<span style="color: gray;">Sin imagen</span>')
    
    image_preview.short_description = 'Vista Previa'
    
    def created_at_formatted(self, obj):
        """Fecha de creación formateada"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    
    created_at_formatted.short_description = 'Creado el'
    
    def updated_at_formatted(self, obj):
        """Fecha de actualización formateada"""
        return obj.updated_at.strftime('%d/%m/%Y %H:%M') if obj.updated_at else '-'
    
    updated_at_formatted.short_description = 'Actualizado el'
    
    actions = ['mark_as_active', 'mark_as_inactive', 'update_low_stock_prices']
    
    def mark_as_active(self, request, queryset):
        """Marcar productos como activos"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} producto(s) marcado(s) como activo(s).', messages.SUCCESS)
    
    mark_as_active.short_description = "Marcar como activos"
    
    def mark_as_inactive(self, request, queryset):
        """Marcar productos como inactivos"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} producto(s) marcado(s) como inactivo(s).', messages.WARNING)
    
    mark_as_inactive.short_description = "Marcar como inactivos"
    
    def update_low_stock_prices(self, request, queryset):
        """Actualizar precios de productos con stock bajo"""
        low_stock_products = queryset.filter(stock_quantity__lte=5)
        if low_stock_products.exists():
            count = low_stock_products.count()
            self.message_user(
                request, 
                f'{count} producto(s) con stock bajo identificado(s). Considerar actualizar precios o reabastecer.',
                messages.WARNING
            )
        else:
            self.message_user(request, 'No hay productos con stock bajo.', messages.INFO)
    
    update_low_stock_prices.short_description = "Verificar productos con stock bajo"


# Inline comentado temporalmente para evitar conflictos
# class OrderItemInline(admin.TabularInline):
#     """Inline para OrderItems en la vista de Order"""
#     model = OrderItem
#     extra = 0
#     fields = ['product', 'quantity', 'unit_price', 'subtotal', 'inventory_impact']
#     readonly_fields = ['subtotal']
#     
#     def subtotal(self, obj):
#         """Calcular subtotal"""
#         return f"S/. {obj.quantity * obj.unit_price:.2f}"
#     
#     subtotal.short_description = 'Subtotal'


# Los siguientes admins están comentados porque ya están registrados en sus módulos específicos
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
# Los admins están definidos en sus módulos específicos

# Configuración adicional del admin
admin.site.site_header = 'Arte Ideas - Administración'
admin.site.site_title = 'Arte Ideas'
admin.site.index_title = 'Panel de Administración'