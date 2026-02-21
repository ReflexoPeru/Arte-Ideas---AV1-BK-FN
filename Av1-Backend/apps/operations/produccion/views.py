from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from datetime import date, timedelta

from .models import OrdenProduccion
from .serializers import OrdenProduccionSerializer
from .filters import OrdenProduccionFilter
# from apps.core.permissions import IsSameTenant  # Comentado temporalmente

class OrdenProduccionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de órdenes de producción"""
    serializer_class = OrdenProduccionSerializer
    permission_classes = [IsAuthenticated]  # IsSameTenant comentado temporalmente
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrdenProduccionFilter
    search_fields = ['numero_op', 'cliente__first_name', 'cliente__last_name', 'pedido__order_number', 'descripcion']
    ordering_fields = ['numero_op', 'fecha_estimada', 'creado_en', 'estado', 'prioridad']
    ordering = ['-creado_en']
    paginate_by = 20
    
    def get_queryset(self):
        """Filtrar órdenes según el tipo de usuario"""
        user = self.request.user
        
        # Superusuarios ven todas las órdenes
        if user.is_superuser:
            return OrdenProduccion.objects.all().select_related('pedido', 'cliente', 'operario', 'tenant')
        
        # Usuarios normales solo ven de su tenant
        if hasattr(user, 'tenant') and user.tenant:
            return OrdenProduccion.objects.filter(
                tenant=user.tenant
            ).select_related('pedido', 'cliente', 'operario')
        
        return OrdenProduccion.objects.none()
    
    def get_serializer_context(self):
        """Pasar contexto necesario al serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        
        if hasattr(self.request.user, 'tenant'):
            context['user_tenant'] = self.request.user.tenant
        
        return context
    
    def perform_create(self, serializer):
        """Asignar automáticamente el tenant al crear"""
        if hasattr(self.request.user, 'tenant') and self.request.user.tenant:
            serializer.save(tenant=self.request.user.tenant, creado_por=self.request.user)
        else:
            serializer.save(creado_por=self.request.user)
    
    def perform_update(self, serializer):
        """Prevenir cambios de tenant en actualizaciones"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Endpoint para obtener estadísticas por estado"""
        queryset = self.get_queryset()
        
        # Calcular estadísticas
        pendientes = queryset.filter(estado='pendiente').count()
        en_proceso = queryset.filter(estado='en_proceso').count()
        terminados = queryset.filter(estado='terminado').count()
        entregados = queryset.filter(estado='entregado').count()
        total = queryset.count()
        
        return Response({
            'pendientes': pendientes,
            'en_proceso': en_proceso,
            'terminados': terminados,
            'entregados': entregados,
            'total': total
        })
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Obtener órdenes filtradas por estado"""
        estado_filter = request.query_params.get('estado', None)
        
        if estado_filter:
            queryset = self.get_queryset().filter(estado=estado_filter)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            # Retornar resumen por estado
            estados_summary = []
            for estado_code, estado_name in OrdenProduccion.ESTADO_CHOICES:
                count = self.get_queryset().filter(estado=estado_code).count()
                estados_summary.append({
                    'estado': estado_code,
                    'estado_name': estado_name,
                    'count': count
                })
            
            return Response({'estados_summary': estados_summary})
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener órdenes agrupadas por tipo de producción"""
        tipo_filter = request.query_params.get('tipo', None)
        
        if tipo_filter:
            queryset = self.get_queryset().filter(tipo=tipo_filter)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            # Retornar resumen por tipo
            tipos_summary = []
            for tipo_code, tipo_name in OrdenProduccion.TIPO_CHOICES:
                count = self.get_queryset().filter(tipo=tipo_code).count()
                tipos_summary.append({
                    'tipo': tipo_code,
                    'tipo_name': tipo_name,
                    'count': count
                })
            
            return Response({'tipos_summary': tipos_summary})
    
    @action(detail=False, methods=['get'])
    def por_operario(self, request):
        """Obtener órdenes agrupadas por operario"""
        operario_id = request.query_params.get('operario_id', None)
        
        if operario_id:
            queryset = self.get_queryset().filter(operario_id=operario_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            # Retornar resumen por operario
            operarios_summary = self.get_queryset().values(
                'operario__id', 'operario__first_name', 'operario__last_name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
            
            return Response({'operarios_summary': list(operarios_summary)})
    
    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """Obtener órdenes vencidas (fecha estimada pasada)"""
        today = date.today()
        vencidas = self.get_queryset().filter(
            fecha_estimada__lt=today,
            estado__in=['pendiente', 'en_proceso']
        ).order_by('fecha_estimada')
        
        page = self.paginate_queryset(vencidas)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(vencidas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximas(self, request):
        """Obtener órdenes próximas a vencer (próximos 7 días)"""
        today = date.today()
        proxima_semana = today + timedelta(days=7)
        
        proximas = self.get_queryset().filter(
            fecha_estimada__range=[today, proxima_semana],
            estado__in=['pendiente', 'en_proceso']
        ).order_by('fecha_estimada')
        
        page = self.paginate_queryset(proximas)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(proximas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de la orden de producción"""
        orden = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(OrdenProduccion.ESTADO_CHOICES):
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estado_anterior = orden.estado
        orden.estado = nuevo_estado
        orden.save()
        
        return Response({
            'message': f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
            'estado_anterior': estado_anterior,
            'estado_nuevo': nuevo_estado
        })
    
    @action(detail=True, methods=['post'])
    def marcar_completado(self, request, pk=None):
        """Marcar orden como terminada"""
        orden = self.get_object()
        
        if orden.estado == 'terminado':
            return Response(
                {'error': 'La orden ya está terminada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orden.estado = 'terminado'
        orden.save()
        
        return Response({'message': 'Orden marcada como terminada'})
    
    @action(detail=False, methods=['get'])
    def resumen_produccion(self, request):
        """Obtener resumen completo de producción"""
        queryset = self.get_queryset()
        
        # Totales generales
        total_ordenes = queryset.count()
        
        # Por estado
        estados = {}
        for estado_code, estado_name in OrdenProduccion.ESTADO_CHOICES:
            count = queryset.filter(estado=estado_code).count()
            estados[estado_code] = {
                'name': estado_name,
                'count': count
            }
        
        # Por tipo
        tipos = {}
        for tipo_code, tipo_name in OrdenProduccion.TIPO_CHOICES:
            count = queryset.filter(tipo=tipo_code).count()
            tipos[tipo_code] = {
                'name': tipo_name,
                'count': count
            }
        
        # Órdenes vencidas
        today = date.today()
        vencidas_count = queryset.filter(
            fecha_estimada__lt=today,
            estado__in=['pendiente', 'en_proceso']
        ).count()
        
        # Próximas a vencer
        proxima_semana = today + timedelta(days=7)
        proximas_count = queryset.filter(
            fecha_estimada__range=[today, proxima_semana],
            estado__in=['pendiente', 'en_proceso']
        ).count()
        
        return Response({
            'total_ordenes': total_ordenes,
            'estados': estados,
            'tipos': tipos,
            'ordenes_vencidas': vencidas_count,
            'ordenes_proximas': proximas_count
        })