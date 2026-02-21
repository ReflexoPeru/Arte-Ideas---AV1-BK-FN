"""
Views del Módulo de Pedidos - Arte Ideas Commerce
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q, F, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Order, OrderItem, OrderPayment, OrderStatusHistory
from .serializers import (
    OrderSerializer, OrderListSerializer, OrderItemSerializer, 
    OrderPaymentSerializer, OrderStatusHistorySerializer,
    OrderSummarySerializer, OrderStatisticsSerializer
)
from .filters import OrderFilter


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de pedidos
    
    Proporciona operaciones CRUD completas para pedidos con:
    - Filtrado avanzado por estado, tipo, fechas
    - Búsqueda por texto en múltiples campos
    - Resumen de totales y estadísticas
    - Gestión de estados y pagos
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = [
        'order_number', 'cliente__nombres', 'cliente__apellidos',
        'cliente__email', 'cliente__telefono', 'cliente__dni', 'cliente__razon_social'
    ]
    ordering_fields = [
        'order_number', 'order_date', 'start_date', 'delivery_date', 'total',
        'status', 'cliente__nombres', 'cliente__apellidos'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """Obtener pedidos del tenant actual"""
        user = self.request.user
        queryset = Order.objects.select_related(
            'cliente', 'contrato', 'created_by'
        ).prefetch_related('items', 'payments')
        
        if user.tenant is None:
            # Super admin puede ver todos los pedidos
            return queryset
        return queryset.filter(tenant=user.tenant)
    
    def perform_create(self, serializer):
        """Crear pedido con tenant y usuario actual"""
        user = self.request.user
        if user.tenant is None:
            # Super admin debe especificar el tenant
            tenant = serializer.validated_data.get('tenant')
            if not tenant:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'tenant': 'El tenant es requerido'})
            serializer.save(tenant=tenant, created_by=user)
        else:
            serializer.save(tenant=user.tenant, created_by=user)
    
    def perform_update(self, serializer):
        """Actualizar pedido manteniendo tenant"""
        user = self.request.user
        if user.tenant is not None:
            # Para usuarios normales, mantener el tenant
            serializer.save(tenant=user.tenant)
        else:
            # Super admin puede cambiar el tenant si lo especifica
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtener estadísticas completas de pedidos
        """
        queryset = self.get_queryset()
        
        # Totales generales
        totals = queryset.aggregate(
            total_orders=Count('id'),
            total_amount=Sum('total'),
            total_paid=Sum('paid_amount'),
            total_balance=Sum('balance')
        )
        
        # Contadores por estado
        status_counts = {}
        for status_code, status_name in Order.ORDER_STATUS_CHOICES:
            count = queryset.filter(status=status_code).count()
            status_counts[status_code] = {
                'name': status_name,
                'count': count
            }
        
        # Contadores por tipo de documento
        doc_type_counts = {}
        for doc_type_code, doc_type_name in Order.DOCUMENT_TYPE_CHOICES:
            count = queryset.filter(document_type=doc_type_code).count()
            doc_type_counts[doc_type_code] = {
                'name': doc_type_name,
                'count': count
            }
        
        # Pedidos atrasados
        today = timezone.now().date()
        overdue_count = queryset.filter(
            delivery_date__lt=today,
            status__in=['pendiente', 'confirmado', 'en_proceso']
        ).count()
        
        # Próximas entregas (7 días)
        next_week = today + timedelta(days=7)
        upcoming_deliveries = queryset.filter(
            delivery_date__range=[today, next_week],
            status__in=['pendiente', 'confirmado', 'en_proceso']
        ).count()
        
        # Estadísticas por mes (últimos 6 meses)
        monthly_stats = []
        for i in range(6):
            month_start = (timezone.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start.replace(month=month_start.month % 12 + 1) - timedelta(days=1))
            
            month_orders = queryset.filter(
                order_date__range=[month_start.date(), month_end.date()]
            )
            
            monthly_stats.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'orders': month_orders.count(),
                'total_amount': month_orders.aggregate(Sum('total'))['total__sum'] or 0
            })
        
        data = {
            'totals': {
                'total_orders': totals['total_orders'] or 0,
                'total_amount': float(totals['total_amount'] or 0),
                'total_paid': float(totals['total_paid'] or 0),
                'total_balance': float(totals['total_balance'] or 0),
                'pending_orders': queryset.filter(status='pendiente').count(),
                'in_process_orders': queryset.filter(status='en_proceso').count(),
                'completed_orders': queryset.filter(status='completado').count(),
                'overdue_orders': overdue_count,
            },
            'status_counts': status_counts,
            'document_type_counts': doc_type_counts,
            'overdue_orders': overdue_count,
            'upcoming_deliveries': upcoming_deliveries,
            'monthly_stats': monthly_stats
        }
        
        serializer = OrderStatisticsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """
        Obtener resumen básico de pedidos
        """
        queryset = self.get_queryset()
        
        # Calcular totales básicos
        totals = queryset.aggregate(
            total_orders=Count('id'),
            total_amount=Sum('total'),
            total_paid=Sum('paid_amount'),
            total_balance=Sum('balance')
        )
        
        # Contadores por estado principales
        pending_orders = queryset.filter(status='pendiente').count()
        in_process_orders = queryset.filter(status='en_proceso').count()
        completed_orders = queryset.filter(status='completado').count()
        overdue_orders = queryset.filter(status='atrasado').count()
        
        summary_data = {
            'total_orders': totals['total_orders'] or 0,
            'total_amount': totals['total_amount'] or 0,
            'total_paid': totals['total_paid'] or 0,
            'total_balance': totals['total_balance'] or 0,
            'pending_orders': pending_orders,
            'in_process_orders': in_process_orders,
            'completed_orders': completed_orders,
            'overdue_orders': overdue_orders,
        }
        
        serializer = OrderSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def atrasados(self, request):
        """Obtener pedidos atrasados"""
        today = timezone.now().date()
        
        overdue_orders = self.get_queryset().filter(
            delivery_date__lt=today,
            status__in=['pendiente', 'confirmado', 'en_proceso']
        ).order_by('delivery_date')
        
        page = self.paginate_queryset(overdue_orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(overdue_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximas_entregas(self, request):
        """Obtener próximas entregas (7 días)"""
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        
        upcoming_orders = self.get_queryset().filter(
            delivery_date__range=[today, next_week],
            status__in=['pendiente', 'confirmado', 'en_proceso']
        ).order_by('delivery_date')
        
        page = self.paginate_queryset(upcoming_orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(upcoming_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Obtener pedidos filtrados por estado"""
        status_filter = request.query_params.get('status', None)
        
        if status_filter:
            queryset = self.get_queryset().filter(status=status_filter)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            # Retornar resumen por estado
            status_summary = []
            for status_code, status_name in Order.ORDER_STATUS_CHOICES:
                count = self.get_queryset().filter(status=status_code).count()
                total = self.get_queryset().filter(status=status_code).aggregate(
                    Sum('total')
                )['total__sum'] or 0
                
                status_summary.append({
                    'status': status_code,
                    'status_name': status_name,
                    'count': count,
                    'total_amount': float(total)
                })
            
            return Response({'status_summary': status_summary})
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado del pedido"""
        order = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason', '')
        
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Registrar cambio en historial
        OrderStatusHistory.objects.create(
            order=order,
            previous_status=order.status,
            new_status=new_status,
            reason=reason,
            changed_by=request.user
        )
        
        order.status = new_status
        order.save()
        
        return Response({'message': f'Estado cambiado a {new_status}'})
    
    @action(detail=True, methods=['post'])
    def marcar_completado(self, request, pk=None):
        """Marcar pedido como completado"""
        order = self.get_object()
        
        if order.status == 'completado':
            return Response(
                {'error': 'El pedido ya está completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Registrar cambio en historial
        OrderStatusHistory.objects.create(
            order=order,
            previous_status=order.status,
            new_status='completado',
            reason='Marcado como completado',
            changed_by=request.user
        )
        
        order.status = 'completado'
        order.save()
        
        return Response({'message': 'Pedido marcado como completado'})
    
    @action(detail=True, methods=['post'])
    def marcar_cancelado(self, request, pk=None):
        """Marcar pedido como cancelado"""
        order = self.get_object()
        reason = request.data.get('reason', 'Cancelado por usuario')
        
        if order.status == 'cancelado':
            return Response(
                {'error': 'El pedido ya está cancelado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if order.status == 'completado':
            return Response(
                {'error': 'No se puede cancelar un pedido completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Registrar cambio en historial
        OrderStatusHistory.objects.create(
            order=order,
            previous_status=order.status,
            new_status='cancelado',
            reason=reason,
            changed_by=request.user
        )
        
        order.status = 'cancelado'
        order.save()
        
        return Response({'message': 'Pedido marcado como cancelado'})
    
    @action(detail=True, methods=['get'])
    def pagos(self, request, pk=None):
        """Obtener pagos del pedido"""
        order = self.get_object()
        payments = OrderPayment.objects.filter(order=order)
        serializer = OrderPaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def registrar_pago(self, request, pk=None):
        """Registrar nuevo pago para el pedido"""
        order = self.get_object()
        data = request.data.copy()
        data['order'] = order.id
        data['registered_by'] = request.user.id
        
        serializer = OrderPaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def historial_estados(self, request, pk=None):
        """Obtener historial de cambios de estado"""
        order = self.get_object()
        history = OrderStatusHistory.objects.filter(order=order)
        serializer = OrderStatusHistorySerializer(history, many=True)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de items de pedido"""
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name', 'product_description', 'product_code']
    filterset_fields = ['order', 'affects_inventory']
    ordering = ['-created_at']

    def get_queryset(self):
        """Obtener items del tenant actual"""
        user = self.request.user
        queryset = OrderItem.objects.select_related('order')
        
        if user.tenant is None:
            # Super admin puede ver todos los items
            return queryset
        return queryset.filter(order__tenant=user.tenant)

    def perform_create(self, serializer):
        """Crear item con tenant automático"""
        user = self.request.user
        if user.tenant is None:
            # Super admin debe obtener el tenant del order
            order = serializer.validated_data.get('order')
            if order and order.tenant:
                serializer.save(tenant=order.tenant)
            else:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'order': 'El pedido debe tener un tenant válido'})
        else:
            serializer.save(tenant=user.tenant)


class OrderPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pagos de pedidos"""
    serializer_class = OrderPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference_number', 'notes']
    filterset_fields = ['order', 'payment_method', 'payment_date']
    ordering = ['-payment_date']

    def get_queryset(self):
        """Obtener pagos del tenant actual"""
        user = self.request.user
        queryset = OrderPayment.objects.select_related('order', 'registered_by')
        
        if user.tenant is None:
            # Super admin puede ver todos los pagos
            return queryset
        return queryset.filter(order__tenant=user.tenant)

    def perform_create(self, serializer):
        """Crear pago con usuario actual"""
        serializer.save(registered_by=self.request.user)


class OrderStatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consulta del historial de estados"""
    serializer_class = OrderStatusHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'new_status']
    ordering = ['-changed_at']

    def get_queryset(self):
        """Obtener historial del tenant actual"""
        user = self.request.user
        queryset = OrderStatusHistory.objects.select_related('order', 'changed_by')
        
        if user.tenant is None:
            # Super admin puede ver todo el historial
            return queryset
        return queryset.filter(order__tenant=user.tenant)
