"""
Administración del Módulo de Inventario - Arte Ideas Commerce
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum

from .models import (
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
)


class BaseInventarioAdmin(admin.ModelAdmin):
    """Administración base para todos los modelos de inventario"""
    list_display = [
        'nombre_producto', 'stock_badge', 'stock_minimo',
        'costo_unitario', 'precio_venta', 'costo_total_display',
        'proveedor', 'is_active'
    ]
    list_filter = ['is_active', 'proveedor', 'fecha_ultima_compra']
    search_fields = ['nombre_producto', 'codigo_producto', 'proveedor']
    
    def get_readonly_fields(self, request, obj=None):
        """Personalizar campos de solo lectura según el usuario"""
        readonly = ['costo_total', 'alerta_stock', 'fecha_creacion', 'fecha_actualizacion']
        # Para usuarios normales, el tenant es de solo lectura (se asigna automáticamente)
        if request.user.role != 'super_admin':
            readonly.append('tenant')
        return readonly
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets según el usuario"""
        fieldsets = (
            ('Información Básica', {
                'fields': (
                    'nombre_producto', 'codigo_producto', 'ubicacion'
                )
            }),
            ('Stock', {
                'fields': (
                    'stock_disponible', 'stock_minimo', 'alerta_stock'
                )
            }),
            ('Precios', {
                'fields': (
                    'costo_unitario', 'precio_venta', 'costo_total'
                )
            }),
            ('Proveedor', {
                'fields': (
                    'proveedor', 'fecha_ultima_compra'
                )
            }),
            ('Estado', {
                'fields': (
                    'is_active',
                )
            }),
            ('Metadatos', {
                'fields': (
                    'fecha_creacion', 'fecha_actualizacion'
                ),
                'classes': ('collapse',)
            })
        )
        
        # Agregar campo tenant solo para super_admin
        if request.user.role == 'super_admin':
            # Insertar campo tenant al inicio
            fieldsets = (
                ('Estudio Fotográfico', {
                    'fields': ('tenant',)
                }),
            ) + fieldsets
        
        return fieldsets
    
    def stock_badge(self, obj):
        """Mostrar stock con badge de color según nivel"""
        # Manejar casos donde los valores pueden ser None
        stock_disponible = obj.stock_disponible or 0
        stock_minimo = obj.stock_minimo or 0
        
        if obj.alerta_stock:
            color = '#dc3545'  # Rojo para alerta
            icon = '⚠️'
        elif stock_disponible <= stock_minimo * 1.5:
            color = '#ffc107'  # Amarillo para advertencia
            icon = '⚡'
        else:
            color = '#28a745'  # Verde para normal
            icon = '✅'
        
        return format_html(
            '{} <span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            icon,
            color,
            stock_disponible
        )
    stock_badge.short_description = 'Stock Disponible'
    
    def costo_total_display(self, obj):
        """Mostrar costo total formateado"""
        costo_total = obj.costo_total or 0
        return f'S/ {costo_total:,.2f}'
    costo_total_display.short_description = 'Costo Total'
    
    # 🟢 CORRECCIÓN DE VISIBILIDAD: El SuperAdmin ve todos los productos.
    def get_queryset(self, request):
        """
        Filtrar por tenant del usuario. 
        Permite al 'super_admin' ver todos los registros.
        """
        qs = super().get_queryset(request)
        
        # 1. Si el usuario es SuperAdmin, retorna el queryset completo (ve todo)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return qs
            
        # 2. Si el usuario es normal y tiene un tenant asignado, filtra por ese tenant
        if hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
            
        # 3. Si es un usuario sin tenant, no devuelve nada
        return qs.none() 
    
    def save_model(self, request, obj, form, change):
        """Guardar con tenant actual"""
        if not change:  # Solo en creación
            if request.user.role == 'super_admin':
                # Super admin debe especificar tenant manualmente (ya está en el formulario)
                # Si no se especificó, el formulario mostrará el error de validación del modelo
                pass  # El campo tenant es requerido en el modelo, Django validará automáticamente
            elif hasattr(request.user, 'tenant') and request.user.tenant:
                # Usuarios normales: asignar tenant automáticamente
                obj.tenant = request.user.tenant
            else:
                # Usuario sin tenant asignado - asignar un tenant por defecto o mostrar error
                # Por ahora, si el usuario no tiene tenant, no se puede crear el producto
                # Esto debería ser manejado por la validación del formulario
                pass
        super().save_model(request, obj, form, change)


# CATEGORÍA: ENMARCADOS
@admin.register(MolduraListon)
class MolduraListonAdmin(BaseInventarioAdmin):
    """Administración de Moldura (Listón)"""
    list_display = BaseInventarioAdmin.list_display + [
        'nombre_moldura', 'ancho', 'color', 'material'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'nombre_moldura', 'ancho', 'color', 'material'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de MolduraListon"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'nombre_moldura', 'ancho', 'color', 'material'
                )
            })
        )
        return tuple(fieldsets)


@admin.register(MolduraPrearmada)
class MolduraPrearmadaAdmin(BaseInventarioAdmin):
    """Administración de Moldura Prearmada"""
    list_display = BaseInventarioAdmin.list_display + [
        'dimensiones', 'color', 'material'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'dimensiones', 'color', 'material'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de MolduraPrearmada"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'dimensiones', 'color', 'material'
                )
            })
        )
        return tuple(fieldsets)


@admin.register(VidrioTapaMDF)
class VidrioTapaMDFAdmin(BaseInventarioAdmin):
    """Administración de Vidrio o Tapa MDF"""
    list_display = BaseInventarioAdmin.list_display + [
        'tipo_material', 'tipo_vidrio', 'grosor', 'tamaño'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'tipo_material', 'tipo_vidrio', 'grosor', 'tamaño'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de VidrioTapaMDF"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'tipo_material', 'tipo_vidrio', 'grosor', 'tamaño'
                )
            })
        )
        return tuple(fieldsets)


@admin.register(Paspartu)
class PaspartuAdmin(BaseInventarioAdmin):
    """Administración de Paspartú"""
    list_display = BaseInventarioAdmin.list_display + [
        'tipo_material', 'tamaño', 'grosor', 'color'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'tipo_material', 'tamaño', 'grosor', 'color'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de Paspartu"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'tipo_material', 'tamaño', 'grosor', 'color'
                )
            })
        )
        return tuple(fieldsets)


# CATEGORÍA: MINILAB
@admin.register(Minilab)
class MinilabAdmin(BaseInventarioAdmin):
    """Administración de Minilab"""
    list_display = BaseInventarioAdmin.list_display + [
        'tipo_insumo', 'nombre_tipo', 'tamaño_presentacion', 'fecha_compra'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'tipo_insumo', 'nombre_tipo', 'tamaño_presentacion', 'fecha_compra'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de Minilab"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'tipo_insumo', 'nombre_tipo', 'tamaño_presentacion', 'fecha_compra'
                )
            })
        )
        return tuple(fieldsets)


# CATEGORÍA: GRADUACIONES
@admin.register(Cuadro)
class CuadroAdmin(BaseInventarioAdmin):
    """Administración de Cuadro"""
    list_display = BaseInventarioAdmin.list_display + [
        'formato', 'dimensiones', 'material'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'formato', 'dimensiones', 'material'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de Cuadro"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'formato', 'dimensiones', 'material'
                )
            })
        )
        return tuple(fieldsets)


@admin.register(Anuario)
class AnuarioAdmin(BaseInventarioAdmin):
    """Administración de Anuario"""
    list_display = BaseInventarioAdmin.list_display + [
        'formato', 'paginas', 'tipo_tapa'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'formato', 'paginas', 'tipo_tapa'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de Anuario"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'formato', 'paginas', 'tipo_tapa'
                )
            })
        )
        return tuple(fieldsets)


# CATEGORÍA: CORTE LÁSER
@admin.register(CorteLaser)
class CorteLaserAdmin(BaseInventarioAdmin):
    """Administración de Corte Láser"""
    list_display = BaseInventarioAdmin.list_display + [
        'producto', 'tipo', 'tamaño', 'color', 'unidad'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'producto', 'tipo', 'tamaño', 'color', 'unidad'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de CorteLaser"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'producto', 'tipo', 'tamaño', 'color', 'unidad'
                )
            })
        )
        return tuple(fieldsets)


# CATEGORÍA: ACCESORIOS
@admin.register(MarcoAccesorio)
class MarcoAccesorioAdmin(BaseInventarioAdmin):
    """Administración de Marco y Accesorio"""
    list_display = BaseInventarioAdmin.list_display + [
        'nombre_moldura', 'tipo_moldura', 'material', 'color'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'tipo_moldura', 'material', 'color'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de MarcoAccesorio"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'nombre_moldura', 'tipo_moldura', 'material', 'color', 'dimensiones'
                )
            })
        )
        return tuple(fieldsets)


@admin.register(HerramientaGeneral)
class HerramientaGeneralAdmin(BaseInventarioAdmin):
    """Administración de Herramienta General"""
    list_display = BaseInventarioAdmin.list_display + [
        'nombre_herramienta', 'marca', 'tipo_material'
    ]
    list_filter = BaseInventarioAdmin.list_filter + [
        'marca', 'tipo_material'
    ]
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets con especificaciones de HerramientaGeneral"""
        fieldsets = list(super().get_fieldsets(request, obj))
        # 🟢 CORRECCIÓN: Se eliminó el paréntesis externo de la tupla anidada.
        fieldsets.insert(1, 
            ('Especificaciones', {
                'fields': (
                    'nombre_herramienta', 'marca', 'tipo_material'
                )
            })
        )
        return tuple(fieldsets)