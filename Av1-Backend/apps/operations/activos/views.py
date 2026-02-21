"""
Views del Módulo de Activos - Arte Ideas Operations
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F
from datetime import date, timedelta

from .models import Activo, Financiamiento, Mantenimiento, Repuesto
from .serializers import (
    ActivoSerializer, FinanciamientoSerializer, 
    MantenimientoSerializer, RepuestoSerializer
)
from .permissions import ActivosPermission, MantenimientoPermission, RepuestosPermission


@api_view(['GET'])
def dashboard_activos(request):
    """API endpoint para obtener métricas principales de activos"""
    
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Calcular métricas principales
    total_activos = Activo.objects.count()
    activos_activos = Activo.objects.filter(estado='activo').count()
    activos_mantenimiento = Activo.objects.filter(estado='en mantenimiento').count()
    
    # Valor total de activos
    valor_total = Activo.objects.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
    
    # Próximos mantenimientos (30 días)
    today = date.today()
    proximos_30_dias = today + timedelta(days=30)
    proximos_mantenimientos = Mantenimiento.objects.filter(
        proxima_fecha_mantenimiento__range=[today, proximos_30_dias],
        estado_del_mantenimiento='programado'
    ).count()
    
    # Repuestos con stock bajo
    repuestos_bajo_stock = Repuesto.objects.filter(
        stock_actual__lte=F('stock_minimo')
    ).count()
    
    # Financiamientos activos
    financiamientos_activos = Financiamiento.objects.filter(estado='activo').count()
    
    data = {
        'total_activos': total_activos,
        'activos_activos': activos_activos,
        'activos_mantenimiento': activos_mantenimiento,
        'valor_total_activos': float(valor_total),
        'proximos_mantenimientos': proximos_mantenimientos,
        'repuestos_bajo_stock': repuestos_bajo_stock,
        'financiamientos_activos': financiamientos_activos,
    }
    
    return Response(data)


class ActivoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de activos"""
    queryset = Activo.objects.all()
    serializer_class = ActivoSerializer
    permission_classes = [IsAuthenticated, ActivosPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'proveedor', 'categoria']
    ordering_fields = ['nombre', 'fecha_compra', 'costo_total', 'estado']
    ordering = ['-fecha_compra']
    filterset_fields = ['categoria', 'estado', 'tipo_pago']
    
    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtener activos agrupados por categoría"""
        categoria = request.query_params.get('categoria', None)
        
        if categoria:
            activos = self.get_queryset().filter(categoria=categoria)
            serializer = self.get_serializer(activos, many=True)
            return Response(serializer.data)
        else:
            # Retornar resumen por categoría
            categorias = {}
            for categoria_code, categoria_name in Activo.CATEGORIAS:
                count = self.get_queryset().filter(categoria=categoria_code).count()
                valor_total = self.get_queryset().filter(categoria=categoria_code).aggregate(
                    Sum('costo_total')
                )['costo_total__sum'] or 0
                
                categorias[categoria_code] = {
                    'name': categoria_name,
                    'count': count,
                    'valor_total': float(valor_total)
                }
            return Response({'categorias': categorias})
    
    @action(detail=False, methods=['get'])
    def depreciacion_report(self, request):
        """Generar reporte de depreciación"""
        activos = self.get_queryset()
        reporte = []
        
        for activo in activos:
            serializer = self.get_serializer(activo)
            data = serializer.data
            reporte.append({
                'nombre': activo.nombre,
                'costo_original': float(activo.costo_total),
                'valor_actual': data['valor_actual'],
                'depreciacion_acumulada': data['depreciacion_acumulada'],
                'meses_transcurridos': data['meses_transcurridos'],
                'vida_util': activo.vida_util
            })
        
        return Response({'reporte_depreciacion': reporte})
    
    @action(detail=False, methods=['get'])
    def mantenimientos_pendientes(self, request):
        """Obtener activos con mantenimientos pendientes"""
        today = date.today()
        activos_con_mantenimiento = self.get_queryset().filter(
            mantenimientos__proxima_fecha_mantenimiento__lte=today,
            mantenimientos__estado_del_mantenimiento='programado'
        ).distinct()
        
        serializer = self.get_serializer(activos_con_mantenimiento, many=True)
        return Response(serializer.data)


class FinanciamientoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de financiamientos"""
    queryset = Financiamiento.objects.all()
    serializer_class = FinanciamientoSerializer
    permission_classes = [IsAuthenticated, ActivosPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['activo__nombre', 'entidad_financiera']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_financiado']
    ordering = ['-fecha_inicio']
    filterset_fields = ['tipo_pago', 'estado', 'entidad_financiera']
    
    @action(detail=False, methods=['get'])
    def resumen_financiero(self, request):
        """Obtener resumen financiero de todos los financiamientos"""
        financiamientos = self.get_queryset()
        
        total_financiado = financiamientos.aggregate(Sum('monto_financiado'))['monto_financiado__sum'] or 0
        cuota_mensual_total = financiamientos.filter(estado='activo').aggregate(
            Sum('cuota_mensual')
        )['cuota_mensual__sum'] or 0
        
        # Calcular saldo pendiente total
        saldo_total = 0
        for financiamiento in financiamientos.filter(estado='activo'):
            serializer = self.get_serializer(financiamiento)
            saldo_total += serializer.data['saldo_pendiente']
        
        return Response({
            'total_financiado': float(total_financiado),
            'cuota_mensual_total': float(cuota_mensual_total),
            'saldo_pendiente_total': float(saldo_total),
            'financiamientos_activos': financiamientos.filter(estado='activo').count(),
            'financiamientos_pagados': financiamientos.filter(estado='pagado').count()
        })
    
    @action(detail=True, methods=['post'])
    def marcar_pagado(self, request, pk=None):
        """Marcar financiamiento como pagado"""
        financiamiento = self.get_object()
        
        if financiamiento.estado == 'pagado':
            return Response(
                {'error': 'El financiamiento ya está marcado como pagado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        financiamiento.estado = 'pagado'
        financiamiento.save()
        
        return Response({'message': 'Financiamiento marcado como pagado'})


class MantenimientoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de mantenimientos"""
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer
    permission_classes = [IsAuthenticated, MantenimientoPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['activo__nombre', 'proveedor', 'descripcion']
    ordering_fields = ['fecha_mantenimiento', 'proxima_fecha_mantenimiento', 'costo']
    ordering = ['-fecha_mantenimiento']
    filterset_fields = ['tipo_mantenimiento', 'estado_del_mantenimiento', 'estado_del_activo']
    
    @action(detail=False, methods=['get'])
    def proximos(self, request):
        """Obtener próximos mantenimientos"""
        dias = int(request.query_params.get('dias', 30))
        today = date.today()
        fecha_limite = today + timedelta(days=dias)
        
        proximos = self.get_queryset().filter(
            proxima_fecha_mantenimiento__range=[today, fecha_limite],
            estado_del_mantenimiento='programado'
        ).order_by('proxima_fecha_mantenimiento')
        
        serializer = self.get_serializer(proximos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Obtener mantenimientos vencidos"""
        today = date.today()
        vencidos = self.get_queryset().filter(
            proxima_fecha_mantenimiento__lt=today,
            estado_del_mantenimiento='programado'
        ).order_by('proxima_fecha_mantenimiento')
        
        serializer = self.get_serializer(vencidos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marcar mantenimiento como completado"""
        mantenimiento = self.get_object()
        
        if mantenimiento.estado_del_mantenimiento == 'completado':
            return Response(
                {'error': 'El mantenimiento ya está completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Datos para completar el mantenimiento
        proxima_fecha = request.data.get('proxima_fecha_mantenimiento')
        estado_activo = request.data.get('estado_del_activo', 'activo')
        
        mantenimiento.estado_del_mantenimiento = 'completado'
        mantenimiento.estado_del_activo = estado_activo
        
        if proxima_fecha:
            mantenimiento.proxima_fecha_mantenimiento = proxima_fecha
        
        mantenimiento.save()
        
        # Actualizar estado del activo
        activo = mantenimiento.activo
        activo.estado = estado_activo
        activo.save()
        
        return Response({'message': 'Mantenimiento completado exitosamente'})


class RepuestoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de repuestos"""
    queryset = Repuesto.objects.all()
    serializer_class = RepuestoSerializer
    permission_classes = [IsAuthenticated, RepuestosPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo', 'proveedor', 'descripcion']
    ordering_fields = ['nombre', 'stock_actual', 'costo_unitario']
    ordering = ['nombre']
    filterset_fields = ['categoria', 'ubicacion', 'proveedor']
    
    @action(detail=False, methods=['get'])
    def alertas_stock(self, request):
        """Obtener repuestos con stock bajo"""
        alertas = self.get_queryset().filter(
            stock_actual__lte=F('stock_minimo')
        ).order_by('stock_actual')
        
        serializer = self.get_serializer(alertas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sin_stock(self, request):
        """Obtener repuestos sin stock"""
        sin_stock = self.get_queryset().filter(stock_actual=0)
        
        serializer = self.get_serializer(sin_stock, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def actualizar_stock(self, request, pk=None):
        """Actualizar stock de repuesto"""
        repuesto = self.get_object()
        cantidad = request.data.get('cantidad', 0)
        operacion = request.data.get('operacion', 'agregar')  # agregar o quitar
        motivo = request.data.get('motivo', 'Ajuste manual')
        
        try:
            cantidad = int(cantidad)
            
            if operacion == 'quitar':
                if repuesto.stock_actual < cantidad:
                    return Response(
                        {'error': f'Stock insuficiente. Stock actual: {repuesto.stock_actual}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                repuesto.stock_actual -= cantidad
            else:  # agregar
                repuesto.stock_actual += cantidad
            
            repuesto.save()
            
            return Response({
                'message': f'Stock actualizado. Nuevo stock: {repuesto.stock_actual}',
                'stock_anterior': repuesto.stock_actual - (cantidad if operacion == 'agregar' else -cantidad),
                'stock_actual': repuesto.stock_actual,
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
    def resumen_inventario(self, request):
        """Obtener resumen del inventario de repuestos"""
        repuestos = self.get_queryset()
        
        total_repuestos = repuestos.count()
        valor_total = sum(r.stock_actual * r.costo_unitario for r in repuestos)
        alertas_stock = repuestos.filter(stock_actual__lte=F('stock_minimo')).count()
        sin_stock = repuestos.filter(stock_actual=0).count()
        
        # Resumen por categoría
        categorias = {}
        for categoria_code, categoria_name in Repuesto.CATEGORIAS:
            count = repuestos.filter(categoria=categoria_code).count()
            categorias[categoria_code] = {
                'name': categoria_name,
                'count': count
            }
        
        return Response({
            'total_repuestos': total_repuestos,
            'valor_total_inventario': float(valor_total),
            'alertas_stock': alertas_stock,
            'sin_stock': sin_stock,
            'categorias': categorias
        })
