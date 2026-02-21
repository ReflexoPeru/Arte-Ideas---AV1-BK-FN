"""
Administración del Módulo de Pedidos - Arte Ideas Commerce
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone

from .models import Order, OrderItem, OrderPayment, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    """Inline para items de pedido"""
    model = OrderItem
    extra = 1
    fields = [
        'product_name', 'product_code', 'quantity', 
        'unit_price', 'discount_percentage', 'subtotal'
    ]
    readonly_fields = ['subtotal']


class OrderPaymentInline(admin.TabularInline):
    """Inline para pagos de pedido"""
    model = OrderPayment
    extra = 0
    fields = [
        'payment_date', 'amount', 'payment_method', 
        'reference_number', 'registered_by'
    ]
    readonly_fields = ['registered_by']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Administración de pedidos"""
    list_display = [
        'order_number', 'cliente_nombre', 'document_type_display',
        'status_badge', 'delivery_date', 'total', 'balance',
        'payment_status_badge', 'created_at'
    ]
    list_filter = [
        'status', 'document_type', 'client_type', 'payment_status',
        'delivery_date', 'created_at', 'affects_inventory'
    ]
    search_fields = [
        'order_number', 'cliente__nombres', 'cliente__apellidos',
        'cliente__razon_social', 'cliente__email', 'cliente__dni'
    ]
    readonly_fields = [
        'balance', 'payment_status', 'affects_inventory',
        'is_overdue', 'days_until_delivery', 'created_at', 'updated_at'
    ]
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer tenant de solo lectura en ediciones"""
        if obj:  # Si estamos editando
            return self.readonly_fields + ['tenant']
        return self.readonly_fields
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'tenant', 'order_number', 'cliente', 'document_type', 'client_type'
            )
        }),
        ('Detalles del Cliente', {
            'fields': (
                'school_level', 'grade', 'section'
            ),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': (
                'order_date', 'start_date', 'delivery_date', 'scheduled_dates'
            )
        }),
        ('Entrega', {
            'fields': (
                'delivery_address', 'delivery_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Montos', {
            'fields': (
                'subtotal', 'tax', 'total', 'paid_amount', 'balance'
            )
        }),
        ('Estado', {
            'fields': (
                'status', 'payment_status', 'affects_inventory'
            )
        }),
        ('Información Adicional', {
            'fields': (
                'contrato', 'extra_services', 'notes', 'description'
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': (
                'created_by', 'is_overdue', 'days_until_delivery',
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    inlines = [OrderItemInline, OrderPaymentInline]
    date_hierarchy = 'delivery_date'
    
    def cliente_nombre(self, obj):
        """Mostrar nombre completo del cliente"""
        if hasattr(obj, 'cliente') and obj.cliente:
            return obj.cliente.obtener_nombre_completo()
        return "-"
    cliente_nombre.short_description = 'Cliente'
    
    def document_type_display(self, obj):
        """Mostrar tipo de documento con color"""
        colors = {
            'proforma': '#17a2b8',
            'nota_venta': '#28a745',
            'contrato': '#6f42c1'
        }
        color = colors.get(getattr(obj, 'document_type', None), '#6c757d')
        display = getattr(obj, 'get_document_type_display', lambda: "-")()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            display
        )
    document_type_display.short_description = 'Tipo Documento'
    
    def status_badge(self, obj):
        """Mostrar estado con badge de color"""
        colors = {
            'pendiente': '#ffc107',
            'confirmado': '#17a2b8',
            'en_proceso': '#fd7e14',
            'completado': '#28a745',
            'atrasado': '#dc3545',
            'cancelado': '#6c757d'
        }
        color = colors.get(getattr(obj, 'status', None), '#6c757d')
        display = getattr(obj, 'get_status_display', lambda: "-")()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            display
        )
    status_badge.short_description = 'Estado'
    
    def payment_status_badge(self, obj):
        """Mostrar estado de pago con badge"""
        colors = {
            'pendiente': '#dc3545',
            'parcial': '#ffc107',
            'completo': '#28a745'
        }
        color = colors.get(getattr(obj, 'payment_status', None), '#6c757d')
        display = getattr(obj, 'get_payment_status_display', lambda: "-")()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            display
        )
    payment_status_badge.short_description = 'Estado Pago'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
        # Si el usuario no tiene tenant, mostrar solo para superusuarios
        if request.user.is_superuser:
            return qs
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """Guardar con tenant y usuario actual"""
        if not change:  # Solo en creación
            tenant = getattr(request.user, 'tenant', None)
            if not tenant:
                from django.contrib import messages
                from django.core.exceptions import ValidationError
                messages.error(request, 'No se puede crear el pedido: el usuario no tiene un tenant asignado.')
                raise ValidationError('El usuario no tiene un tenant asignado')
            obj.tenant = tenant
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Administración de items de pedido"""
    list_display = [
        'order_number', 'product_name', 'quantity', 
        'unit_price', 'discount_percentage', 'subtotal',
        'affects_inventory'
    ]
    list_filter = [
        'affects_inventory', 'order__status', 'order__document_type'
    ]
    search_fields = [
        'product_name', 'product_code', 'order__order_number'
    ]
    readonly_fields = ['subtotal', 'affects_inventory', 'discount_amount']
    
    def order_number(self, obj):
        """Mostrar número de pedido con enlace"""
        if hasattr(obj, 'order') and obj.order:
            url = reverse('admin:commerce_order_change', args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return "-"
    order_number.short_description = 'Pedido'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if hasattr(request.user, 'tenant'):
            return qs.filter(order__tenant=request.user.tenant)
        return qs


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    """Administración de pagos de pedido"""
    list_display = [
        'order_number', 'payment_date', 'amount', 
        'payment_method', 'reference_number', 'registered_by'
    ]
    list_filter = [
        'payment_method', 'payment_date', 'registered_by'
    ]
    search_fields = [
        'order__order_number', 'reference_number', 'notes'
    ]
    readonly_fields = ['registered_by', 'created_at']
    date_hierarchy = 'payment_date'
    
    def order_number(self, obj):
        """Mostrar número de pedido con enlace"""
        if hasattr(obj, 'order') and obj.order:
            url = reverse('admin:commerce_order_change', args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return "-"
    order_number.short_description = 'Pedido'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if hasattr(request.user, 'tenant'):
            return qs.filter(order__tenant=request.user.tenant)
        return qs
    
    def save_model(self, request, obj, form, change):
        """Guardar con usuario actual"""
        if not change:  # Solo en creación
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Administración del historial de estados"""
    list_display = [
        'order_number', 'previous_status', 'new_status', 
        'changed_by', 'changed_at'
    ]
    list_filter = [
        'previous_status', 'new_status', 'changed_at', 'changed_by'
    ]
    search_fields = [
        'order__order_number', 'reason'
    ]
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'
    
    def order_number(self, obj):
        """Mostrar número de pedido con enlace"""
        if hasattr(obj, 'order') and obj.order:
            url = reverse('admin:commerce_order_change', args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return "-"
    order_number.short_description = 'Pedido'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if hasattr(request.user, 'tenant'):
            return qs.filter(order__tenant=request.user.tenant)
        return qs
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar"""
        return False
