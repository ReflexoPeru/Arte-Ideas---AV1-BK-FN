"""
Views del Commerce App - Arte Ideas
Importaciones centralizadas para compatibilidad
"""

# Importar vistas de pedidos
from .pedidos.views import (
    OrderViewSet, OrderItemViewSet, OrderPaymentViewSet, OrderStatusHistoryViewSet
)

# Importar vistas de inventario
from .inventario.views import (
    dashboard_inventario, metricas_api,
    MolduraListonViewSet, MolduraPrearmadaViewSet, VidrioTapaMDFViewSet,
    PaspartuViewSet, MinilabViewSet, CuadroViewSet, AnuarioViewSet,
    CorteLaserViewSet, MarcoAccesorioViewSet, HerramientaGeneralViewSet
)

# Mantener ProductViewSet básico para compatibilidad con código legacy
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from .models import Product
from .serializers import ProductSerializer
from .permissions import CommercePermission


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet básico para productos legacy
    NOTA: Para nuevos desarrollos, usar los ViewSets específicos del módulo inventario
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, CommercePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'unit_price', 'stock_quantity', 'created_at']
    ordering = ['name']
    filterset_fields = ['product_type', 'is_active']
    
    def get_queryset(self):
        """Obtener productos del tenant actual"""
        user = self.request.user
        if user.tenant is None:
            # Super admin puede ver todos los productos
            return Product.objects.all()
        return Product.objects.filter(tenant=user.tenant)
    
    def perform_create(self, serializer):
        """Crear producto con tenant actual"""
        user = self.request.user
        if user.tenant is None:
            # Super admin debe especificar el tenant
            tenant = serializer.validated_data.get('tenant')
            if not tenant:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'tenant': 'El tenant es requerido'})
            serializer.save(tenant=tenant)
        else:
            serializer.save(tenant=user.tenant)
    
    def perform_update(self, serializer):
        """Actualizar producto manteniendo tenant"""
        user = self.request.user
        if user.tenant is not None:
            # Para usuarios normales, mantener el tenant
            serializer.save(tenant=user.tenant)
        else:
            # Super admin puede cambiar el tenant si lo especifica
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Obtener productos con bajo stock"""
        queryset = self.get_queryset().filter(
            stock_quantity__lte=F('min_stock'),
            is_active=True
        ).order_by('stock_quantity')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_products(self, request):
        """Obtener productos activos"""
        queryset = self.get_queryset().filter(is_active=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Actualizar stock de producto"""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        operation = request.data.get('operation', 'add')  # add o subtract
        
        try:
            quantity = int(quantity)
            if operation == 'subtract':
                if product.stock_quantity < quantity:
                    return Response(
                        {'error': f'Stock insuficiente. Stock actual: {product.stock_quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                product.stock_quantity -= quantity
            else:  # add
                product.stock_quantity += quantity
            
            product.save()
            
            return Response({
                'message': f'Stock actualizado. Nuevo stock: {product.stock_quantity}',
                'stock_actual': product.stock_quantity
            })
        
        except (ValueError, TypeError):
            return Response(
                {'error': 'Cantidad inválida'},
                status=status.HTTP_400_BAD_REQUEST
            )