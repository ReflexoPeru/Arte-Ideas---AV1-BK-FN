"""
Filtros del Módulo de Pedidos - Arte Ideas Commerce
"""
import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Order, OrderItem, OrderPayment


class OrderFilter(django_filters.FilterSet):
    """
    Filtros avanzados para pedidos
    """
    # Filtros por fechas
    order_date = django_filters.DateFilter(field_name='order_date')
    order_date_from = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_to = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    
    start_date = django_filters.DateFilter(field_name='start_date')
    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    
    delivery_date = django_filters.DateFilter(field_name='delivery_date')
    delivery_date_from = django_filters.DateFilter(field_name='delivery_date', lookup_expr='gte')
    delivery_date_to = django_filters.DateFilter(field_name='delivery_date', lookup_expr='lte')
    
    # Filtros por rangos de montos
    total_min = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    
    balance_min = django_filters.NumberFilter(field_name='balance', lookup_expr='gte')
    balance_max = django_filters.NumberFilter(field_name='balance', lookup_expr='lte')
    
    # Filtros por estado
    status = django_filters.ChoiceFilter(choices=Order.ORDER_STATUS_CHOICES)
    status_in = django_filters.MultipleChoiceFilter(
        field_name='status',
        choices=Order.ORDER_STATUS_CHOICES,
        lookup_expr='in'
    )
    
    # Filtros por tipo de documento
    document_type = django_filters.ChoiceFilter(choices=Order.DOCUMENT_TYPE_CHOICES)
    document_type_in = django_filters.MultipleChoiceFilter(
        field_name='document_type',
        choices=Order.DOCUMENT_TYPE_CHOICES,
        lookup_expr='in'
    )
    
    # Filtros por tipo de cliente
    client_type = django_filters.ChoiceFilter(choices=Order.CLIENT_TYPE_CHOICES)
    client_type_in = django_filters.MultipleChoiceFilter(
        field_name='client_type',
        choices=Order.CLIENT_TYPE_CHOICES,
        lookup_expr='in'
    )
    
    # Filtros por estado de pago
    payment_status = django_filters.ChoiceFilter(choices=Order.PAYMENT_STATUS_CHOICES)
    payment_status_in = django_filters.MultipleChoiceFilter(
        field_name='payment_status',
        choices=Order.PAYMENT_STATUS_CHOICES,
        lookup_expr='in'
    )
    
    # Filtros por cliente
    cliente_id = django_filters.NumberFilter(field_name='cliente__id')
    cliente_nombre = django_filters.CharFilter(
        method='filter_cliente_nombre',
        label='Nombre del Cliente'
    )
    
    # Filtros especiales
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')
    upcoming_delivery = django_filters.NumberFilter(method='filter_upcoming_delivery')
    has_balance = django_filters.BooleanFilter(method='filter_has_balance')
    
    # Filtros por contrato
    contrato_id = django_filters.NumberFilter(field_name='contrato__id')
    has_contrato = django_filters.BooleanFilter(method='filter_has_contrato')
    
    class Meta:
        model = Order
        fields = [
            'order_number', 'status', 'document_type', 'client_type',
            'payment_status', 'school_level', 'affects_inventory'
        ]
    
    def filter_cliente_nombre(self, queryset, name, value):
        """Filtrar por nombre completo del cliente"""
        return queryset.filter(
            Q(cliente__nombres__icontains=value) |
            Q(cliente__apellidos__icontains=value) |
            Q(cliente__razon_social__icontains=value)
        )
    
    def filter_overdue(self, queryset, name, value):
        """Filtrar pedidos atrasados"""
        today = timezone.now().date()
        if value:
            return queryset.filter(
                delivery_date__lt=today,
                status__in=['pendiente', 'confirmado', 'en_proceso']
            )
        else:
            return queryset.exclude(
                delivery_date__lt=today,
                status__in=['pendiente', 'confirmado', 'en_proceso']
            )
    
    def filter_upcoming_delivery(self, queryset, name, value):
        """Filtrar pedidos con entrega próxima (en X días)"""
        today = timezone.now().date()
        future_date = today + timedelta(days=value)
        return queryset.filter(
            delivery_date__range=[today, future_date],
            status__in=['pendiente', 'confirmado', 'en_proceso']
        )
    
    def filter_has_balance(self, queryset, name, value):
        """Filtrar pedidos con saldo pendiente"""
        if value:
            return queryset.filter(balance__gt=0)
        else:
            return queryset.filter(balance=0)
    
    def filter_has_contrato(self, queryset, name, value):
        """Filtrar pedidos que tienen contrato asociado"""
        if value:
            return queryset.filter(contrato__isnull=False)
        else:
            return queryset.filter(contrato__isnull=True)


class OrderItemFilter(django_filters.FilterSet):
    """Filtros para items de pedido"""
    
    # Filtros por producto
    product_name = django_filters.CharFilter(lookup_expr='icontains')
    product_code = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por cantidad y precios
    quantity_min = django_filters.NumberFilter(field_name='quantity', lookup_expr='gte')
    quantity_max = django_filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    
    unit_price_min = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gte')
    unit_price_max = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lte')
    
    subtotal_min = django_filters.NumberFilter(field_name='subtotal', lookup_expr='gte')
    subtotal_max = django_filters.NumberFilter(field_name='subtotal', lookup_expr='lte')
    
    # Filtros por descuento
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    discount_min = django_filters.NumberFilter(field_name='discount_percentage', lookup_expr='gte')
    discount_max = django_filters.NumberFilter(field_name='discount_percentage', lookup_expr='lte')
    
    class Meta:
        model = OrderItem
        fields = ['order', 'affects_inventory', 'inventory_item_id']
    
    def filter_has_discount(self, queryset, name, value):
        """Filtrar items con descuento"""
        if value:
            return queryset.filter(discount_percentage__gt=0)
        else:
            return queryset.filter(discount_percentage=0)


class OrderPaymentFilter(django_filters.FilterSet):
    """Filtros para pagos de pedidos"""
    
    # Filtros por fechas
    payment_date = django_filters.DateFilter(field_name='payment_date')
    payment_date_from = django_filters.DateFilter(field_name='payment_date', lookup_expr='gte')
    payment_date_to = django_filters.DateFilter(field_name='payment_date', lookup_expr='lte')
    
    # Filtros por montos
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    # Filtros por método de pago
    payment_method = django_filters.ChoiceFilter(choices=OrderPayment.PAYMENT_METHOD_CHOICES)
    payment_method_in = django_filters.MultipleChoiceFilter(
        field_name='payment_method',
        choices=OrderPayment.PAYMENT_METHOD_CHOICES,
        lookup_expr='in'
    )
    
    # Filtros por referencia
    reference_number = django_filters.CharFilter(lookup_expr='icontains')
    has_reference = django_filters.BooleanFilter(method='filter_has_reference')
    
    class Meta:
        model = OrderPayment
        fields = ['order', 'payment_method', 'registered_by']
    
    def filter_has_reference(self, queryset, name, value):
        """Filtrar pagos que tienen número de referencia"""
        if value:
            return queryset.exclude(reference_number='')
        else:
            return queryset.filter(reference_number='')