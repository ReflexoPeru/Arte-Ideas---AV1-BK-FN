from django.db.models import Sum, Count, Q, F
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
)
from .serializers import (
    MolduraListonSerializer, MolduraPrearmadaSerializer, VidrioTapaMDFSerializer,
    PaspartuSerializer, MinilabSerializer, CuadroSerializer, AnuarioSerializer,
    CorteLaserSerializer, MarcoAccesorioSerializer, HerramientaGeneralSerializer
)
from .permissions import InventarioPermission


@api_view(['GET'])
def dashboard_inventario(request):
    """API endpoint para obtener métricas principales del inventario"""
    
    # Verificar autenticación
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Obtener tenant del usuario
    tenant = request.user.tenant
    if tenant is None:
        return Response(
            {'error': 'Usuario sin tenant asignado. Se requiere un tenant para acceder al inventario.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener todos los modelos de inventario
    modelos_inventario = [
        MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
        Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
    ]
    
    # Calcular métricas principales
    total_productos = 0
    stock_total = 0
    alertas_stock = 0
    valor_total_inventario = 0
    
    for modelo in modelos_inventario:
        # Filtrar por tenant
        productos = modelo.objects.filter(tenant=tenant, is_active=True)
        total_productos += productos.count()
        stock_total += productos.aggregate(Sum('stock_disponible'))['stock_disponible__sum'] or 0
        alertas_stock += productos.filter(stock_disponible__lte=F('stock_minimo')).count()
        
        # Calcular valor total del inventario
        for producto in productos:
            valor_total_inventario += float(producto.costo_total)
    
    # Productos con alertas de stock
    productos_alerta = []
    for modelo in modelos_inventario:
        alertas = modelo.objects.filter(
            tenant=tenant,
            is_active=True,
            stock_disponible__lte=F('stock_minimo')
        )
        for producto in alertas:
            productos_alerta.append({
                'categoria': modelo._meta.verbose_name,
                'nombre': producto.nombre_producto,
                'stock_actual': producto.stock_disponible,
                'stock_minimo': producto.stock_minimo,
                'costo_total': float(producto.costo_total),
            })
    
    data = {
        'total_productos': total_productos,
        'stock_total': stock_total,
        'alertas_stock': alertas_stock,
        'valor_total_inventario': valor_total_inventario,
        'productos_alerta': productos_alerta,
    }
    
    return Response(data)


@api_view(['GET'])
def metricas_api(request):
    """API endpoint para obtener métricas del inventario en formato JSON"""
    
    # Verificar autenticación
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Obtener tenant del usuario
    tenant = request.user.tenant
    if tenant is None:
        return Response(
            {'error': 'Usuario sin tenant asignado. Se requiere un tenant para acceder al inventario.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    modelos_inventario = [
        MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
        Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
    ]
    
    metricas = {
        'total_productos': 0,
        'stock_total': 0,
        'alertas_stock': 0,
        'valor_total_inventario': 0,
        'categorias': {}
    }
    
    for modelo in modelos_inventario:
        # Filtrar por tenant
        productos = modelo.objects.filter(tenant=tenant, is_active=True)
        categoria = modelo._meta.verbose_name_plural
        
        count = productos.count()
        stock = productos.aggregate(Sum('stock_disponible'))['stock_disponible__sum'] or 0
        alertas = productos.filter(stock_disponible__lte=F('stock_minimo')).count()
        
        metricas['total_productos'] += count
        metricas['stock_total'] += stock
        metricas['alertas_stock'] += alertas
        
        # Calcular valor por categoría
        valor_categoria = sum(p.costo_total for p in productos)
        metricas['valor_total_inventario'] += valor_categoria
        
        metricas['categorias'][categoria] = {
            'productos': count,
            'stock': stock,
            'alertas': alertas,
            'valor': float(valor_categoria)
        }
    
    return Response(metricas)

# ViewSets para API REST completa
class BaseInventarioViewSet(viewsets.ModelViewSet):
    """ViewSet base para todos los modelos de inventario"""
    permission_classes = [IsAuthenticated, InventarioPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_producto', 'codigo_producto', 'proveedor']
    ordering_fields = [
        'nombre_producto', 'stock_disponible', 'stock_minimo', 
        'costo_unitario', 'precio_venta', 'fecha_creacion'
    ]
    ordering = ['nombre_producto']
    filterset_fields = ['is_active', 'proveedor']
    
    def get_queryset(self):
        """Obtener productos del tenant actual"""
        user = self.request.user
        if user.tenant is None:
            # Super admin puede ver todos los productos
            return self.queryset.all()
        return self.queryset.filter(tenant=user.tenant)
    
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
    def alertas_stock(self, request):
        """Endpoint para obtener productos con alertas de stock"""
        productos_alerta = self.get_queryset().filter(
            stock_disponible__lte=F('stock_minimo'),
            is_active=True
        ).order_by('stock_disponible')
        
        page = self.paginate_queryset(productos_alerta)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(productos_alerta, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        """Endpoint para obtener productos con stock crítico (menos del 20% del stock mínimo)"""
        productos_bajo_stock = self.get_queryset().filter(
            stock_disponible__lte=F('stock_minimo') * 0.2,
            is_active=True
        ).order_by('stock_disponible')
        
        page = self.paginate_queryset(productos_bajo_stock)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(productos_bajo_stock, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sin_stock(self, request):
        """Endpoint para obtener productos sin stock"""
        productos_sin_stock = self.get_queryset().filter(
            stock_disponible=0,
            is_active=True
        ).order_by('nombre_producto')
        
        page = self.paginate_queryset(productos_sin_stock)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(productos_sin_stock, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def actualizar_stock(self, request, pk=None):
        """Actualizar stock de un producto"""
        producto = self.get_object()
        cantidad = request.data.get('cantidad', 0)
        operacion = request.data.get('operacion', 'agregar')  # agregar o quitar
        motivo = request.data.get('motivo', 'Ajuste manual')
        
        try:
            cantidad = int(cantidad)
            
            if operacion == 'quitar':
                if producto.stock_disponible < cantidad:
                    return Response(
                        {'error': f'Stock insuficiente. Stock actual: {producto.stock_disponible}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                producto.stock_disponible -= cantidad
            else:  # agregar
                producto.stock_disponible += cantidad
            
            producto.save()
            
            return Response({
                'message': f'Stock actualizado. Nuevo stock: {producto.stock_disponible}',
                'stock_anterior': producto.stock_disponible - (cantidad if operacion == 'agregar' else -cantidad),
                'stock_actual': producto.stock_disponible,
                'operacion': operacion,
                'cantidad': cantidad,
                'motivo': motivo
            })
        
        except (ValueError, TypeError):
            return Response(
                {'error': 'Cantidad inválida'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def resumen_categoria(self, request):
        """Obtener resumen de la categoría actual"""
        queryset = self.get_queryset()
        
        resumen = {
            'total_productos': queryset.count(),
            'productos_activos': queryset.filter(is_active=True).count(),
            'stock_total': queryset.aggregate(Sum('stock_disponible'))['stock_disponible__sum'] or 0,
            'valor_total': sum(float(p.costo_total) for p in queryset.filter(is_active=True)),
            'alertas_stock': queryset.filter(
                stock_disponible__lte=F('stock_minimo'),
                is_active=True
            ).count(),
            'sin_stock': queryset.filter(stock_disponible=0, is_active=True).count(),
        }
        
        return Response(resumen)


# ViewSets específicos para cada categoría de inventario

class MolduraListonViewSet(BaseInventarioViewSet):
    """ViewSet para Molduras (Listón)"""
    queryset = MolduraListon.objects.all()
    serializer_class = MolduraListonSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'nombre_moldura', 'ancho', 'color', 'material'
    ]


class MolduraPrearmadaViewSet(BaseInventarioViewSet):
    """ViewSet para Molduras Prearmadas"""
    queryset = MolduraPrearmada.objects.all()
    serializer_class = MolduraPrearmadaSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'dimensiones', 'color', 'material'
    ]


class VidrioTapaMDFViewSet(BaseInventarioViewSet):
    """ViewSet para Vidrios y Tapas MDF"""
    queryset = VidrioTapaMDF.objects.all()
    serializer_class = VidrioTapaMDFSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'tipo_material', 'tipo_vidrio', 'grosor', 'tamaño'
    ]


class PaspartuViewSet(BaseInventarioViewSet):
    """ViewSet para Paspartús"""
    queryset = Paspartu.objects.all()
    serializer_class = PaspartuSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'tipo_material', 'tamaño', 'grosor', 'color'
    ]


class MinilabViewSet(BaseInventarioViewSet):
    """ViewSet para productos de Minilab"""
    queryset = Minilab.objects.all()
    serializer_class = MinilabSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'tipo_insumo', 'nombre_tipo', 'tamaño_presentacion'
    ]
    
    @action(detail=False, methods=['get'])
    def por_tipo_insumo(self, request):
        """Obtener productos agrupados por tipo de insumo"""
        tipo_insumo = request.query_params.get('tipo', None)
        
        if tipo_insumo:
            productos = self.get_queryset().filter(tipo_insumo=tipo_insumo, is_active=True)
            serializer = self.get_serializer(productos, many=True)
            return Response(serializer.data)
        else:
            # Retornar resumen por tipo
            tipos = {}
            for tipo_code, tipo_name in Minilab.TIPOS_INSUMO:
                count = self.get_queryset().filter(tipo_insumo=tipo_code, is_active=True).count()
                tipos[tipo_code] = {
                    'name': tipo_name,
                    'count': count
                }
            return Response({'tipos_insumo': tipos})


class CuadroViewSet(BaseInventarioViewSet):
    """ViewSet para Cuadros"""
    queryset = Cuadro.objects.all()
    serializer_class = CuadroSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'formato', 'dimensiones', 'material'
    ]


class AnuarioViewSet(BaseInventarioViewSet):
    """ViewSet para Anuarios"""
    queryset = Anuario.objects.all()
    serializer_class = AnuarioSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'formato', 'paginas', 'tipo_tapa'
    ]


class CorteLaserViewSet(BaseInventarioViewSet):
    """ViewSet para productos de Corte Láser"""
    queryset = CorteLaser.objects.all()
    serializer_class = CorteLaserSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'producto', 'tipo', 'tamaño', 'color', 'unidad'
    ]
    
    @action(detail=False, methods=['get'])
    def por_tipo_material(self, request):
        """Obtener productos agrupados por tipo de material"""
        tipo = request.query_params.get('tipo', None)
        
        if tipo:
            productos = self.get_queryset().filter(tipo=tipo, is_active=True)
            serializer = self.get_serializer(productos, many=True)
            return Response(serializer.data)
        else:
            # Retornar resumen por tipo
            tipos = {}
            for tipo_code, tipo_name in CorteLaser.TIPOS:
                count = self.get_queryset().filter(tipo=tipo_code, is_active=True).count()
                tipos[tipo_code] = {
                    'name': tipo_name,
                    'count': count
                }
            return Response({'tipos_material': tipos})


class MarcoAccesorioViewSet(BaseInventarioViewSet):
    """ViewSet para Marcos y Accesorios"""
    queryset = MarcoAccesorio.objects.all()
    serializer_class = MarcoAccesorioSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'tipo_moldura', 'material', 'color'
    ]


class HerramientaGeneralViewSet(BaseInventarioViewSet):
    """ViewSet para Herramientas Generales"""
    queryset = HerramientaGeneral.objects.all()
    serializer_class = HerramientaGeneralSerializer
    filterset_fields = BaseInventarioViewSet.filterset_fields + [
        'marca', 'tipo_material'
    ]