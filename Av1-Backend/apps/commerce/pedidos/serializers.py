"""
Serializers del Módulo de Pedidos - Arte Ideas Commerce
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Order, OrderItem, OrderPayment, OrderStatusHistory
from apps.crm.models import Cliente, Contrato

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer para items de pedido"""
    discount_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_description', 'product_code',
            'quantity', 'unit_price', 'discount_percentage', 'subtotal',
            'discount_amount', 'affects_inventory', 'inventory_item_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'subtotal', 'affects_inventory', 'created_at', 'updated_at']


class OrderPaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos de pedido"""
    registered_by_name = serializers.CharField(source='registered_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrderPayment
        fields = [
            'id', 'order', 'payment_date', 'amount', 'payment_method',
            'reference_number', 'notes', 'registered_by', 'registered_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'registered_by_name', 'created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer para historial de estados"""
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    previous_status_display = serializers.CharField(source='get_previous_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'order', 'previous_status', 'previous_status_display',
            'new_status', 'new_status_display', 'reason',
            'changed_by', 'changed_by_name', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer completo para pedidos"""
    cliente_nombre = serializers.CharField(source='cliente.obtener_nombre_completo', read_only=True)
    contrato_numero = serializers.CharField(source='contrato.numero_contrato', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    # Campos calculados
    is_overdue = serializers.ReadOnlyField()
    days_until_delivery = serializers.ReadOnlyField()
    
    # Campos de display
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    client_type_display = serializers.CharField(source='get_client_type_display', read_only=True)
    school_level_display = serializers.CharField(source='get_school_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    # Relaciones anidadas
    items = OrderItemSerializer(many=True, read_only=True)
    payments = OrderPaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'cliente', 'cliente_nombre',
            'document_type', 'document_type_display', 'client_type', 'client_type_display',
            'school_level', 'school_level_display', 'grade', 'section',
            'order_date', 'start_date', 'delivery_date', 'scheduled_dates',
            'delivery_address', 'delivery_notes',
            'subtotal', 'tax', 'total', 'paid_amount', 'balance',
            'payment_status', 'payment_status_display',
            'extra_services', 'status', 'status_display',
            'contrato', 'contrato_numero', 'notes', 'description',
            'affects_inventory', 'created_by', 'created_by_name',
            'is_overdue', 'days_until_delivery',
            'items', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'balance', 'payment_status', 'affects_inventory',
            'is_overdue', 'days_until_delivery', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar fechas
        if data.get('start_date') and data.get('delivery_date'):
            if data['start_date'] > data['delivery_date']:
                raise serializers.ValidationError({
                    'delivery_date': 'La fecha de entrega debe ser posterior a la fecha de inicio'
                })
        
        # Validar campos requeridos según tipo de cliente
        if data.get('client_type') == 'colegio':
            if not data.get('school_level'):
                raise serializers.ValidationError({
                    'school_level': 'El nivel es obligatorio para colegios'
                })
        
        # Validar montos
        if data.get('total', 0) < 0:
            raise serializers.ValidationError({
                'total': 'El total no puede ser negativo'
            })
        
        if data.get('paid_amount', 0) < 0:
            raise serializers.ValidationError({
                'paid_amount': 'El monto pagado no puede ser negativo'
            })
        
        if data.get('paid_amount', 0) > data.get('total', 0):
            raise serializers.ValidationError({
                'paid_amount': 'El monto pagado no puede exceder el total'
            })
        
        return data

    def create(self, validated_data):
        # Asegurar tipos date para campos de fecha
        from datetime import datetime
        from django.utils import timezone
        for key in ('order_date', 'start_date', 'delivery_date'):
            value = validated_data.get(key)
            if value is None and key == 'order_date':
                validated_data[key] = timezone.localdate()
            elif isinstance(value, datetime):
                validated_data[key] = value.date()
        return super().create(validated_data)


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de pedidos"""
    cliente_nombre = serializers.CharField(source='cliente.obtener_nombre_completo', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_delivery = serializers.ReadOnlyField()
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'cliente', 'cliente_nombre',
            'document_type', 'document_type_display',
            'order_date', 'delivery_date', 'total', 'paid_amount', 'balance',
            'status', 'status_display', 'payment_status', 'payment_status_display',
            'is_overdue', 'days_until_delivery', 'items_count',
            'created_at'
        ]


class OrderSummarySerializer(serializers.Serializer):
    """Serializer para resumen de pedidos"""
    total_orders = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_orders = serializers.IntegerField()
    in_process_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    overdue_orders = serializers.IntegerField()


class OrderStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas completas de pedidos"""
    totals = OrderSummarySerializer()
    status_counts = serializers.DictField()
    document_type_counts = serializers.DictField()
    overdue_orders = serializers.IntegerField()
    upcoming_deliveries = serializers.IntegerField()
    monthly_stats = serializers.ListField()
