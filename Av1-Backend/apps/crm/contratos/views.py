"""
Views del Módulo de Contratos - Arte Ideas CRM
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import Contrato, ClausulaContrato, PagoContrato, EstadoContrato
from .serializers import (
    ContratoSerializer, ContratoListSerializer, ClausulaContratoSerializer,
    PagoContratoSerializer, EstadoContratoSerializer, ContratoEstadisticasSerializer
)


class ContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de contratos
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'tipo_servicio', 'cliente']
    search_fields = ['numero_contrato', 'titulo', 'cliente__nombres', 'cliente__apellidos']
    ordering_fields = ['numero_contrato', 'fecha_inicio', 'monto_total', 'creado_en']
    ordering = ['-creado_en']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContratoListSerializer
        return ContratoSerializer

    def get_queryset(self):
        """Filtrar contratos por tenant del usuario"""
        if self.request.user.is_superuser:
            return Contrato.objects.select_related('cliente').all()
        return Contrato.objects.select_related('cliente').filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        """Asignar tenant automáticamente al crear"""
        serializer.save(tenant=self.request.user.tenant)

    def perform_update(self, serializer):
        contrato = self.get_object()
        estado_anterior = contrato.estado
        instancia = serializer.save()
        if 'estado' in serializer.validated_data and instancia.estado != estado_anterior:
            EstadoContrato.objects.create(
                contrato=instancia,
                estado_anterior=estado_anterior,
                estado_nuevo=instancia.estado,
                motivo='',
                cambiado_por=self.request.user
            )

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de contratos"""
        queryset = self.get_queryset()
        
        total_contratos = queryset.count()
        contratos_activos = queryset.filter(estado='activo').count()
        contratos_completados = queryset.filter(estado='completado').count()
        contratos_cancelados = queryset.filter(estado='cancelado').count()
        
        # Montos
        monto_total = queryset.aggregate(total=Sum('monto_total'))['total'] or 0
        monto_adelantos = queryset.aggregate(total=Sum('adelanto'))['total'] or 0
        monto_pendiente = queryset.aggregate(total=Sum('saldo_pendiente'))['total'] or 0
        
        # Contratos por tipo de servicio
        por_tipo = {}
        for choice in Contrato.TIPO_SERVICIO_CHOICES:
            tipo_codigo = choice[0]
            tipo_nombre = choice[1]
            count = queryset.filter(tipo_servicio=tipo_codigo).count()
            por_tipo[tipo_codigo] = {'nombre': tipo_nombre, 'cantidad': count}
        
        # Contratos vencidos
        hoy = timezone.now().date()
        contratos_vencidos = queryset.filter(fecha_fin__lt=hoy, estado='activo').count()
        
        data = {
            'total_contratos': total_contratos,
            'contratos_activos': contratos_activos,
            'contratos_completados': contratos_completados,
            'contratos_cancelados': contratos_cancelados,
            'contratos_vencidos': contratos_vencidos,
            'montos': {
                'total': float(monto_total),
                'adelantos': float(monto_adelantos),
                'pendiente': float(monto_pendiente)
            },
            'por_tipo_servicio': por_tipo
        }
        
        serializer = ContratoEstadisticasSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Obtener contratos vencidos"""
        hoy = timezone.now().date()
        queryset = self.get_queryset().filter(fecha_fin__lt=hoy, estado='activo')
        serializer = ContratoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def proximos_vencer(self, request):
        """Obtener contratos próximos a vencer (30 días)"""
        from datetime import timedelta
        hoy = timezone.now().date()
        fecha_limite = hoy + timedelta(days=30)
        
        queryset = self.get_queryset().filter(
            fecha_fin__gte=hoy,
            fecha_fin__lte=fecha_limite,
            estado='activo'
        )
        serializer = ContratoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado del contrato"""
        contrato = self.get_object()
        nuevo_estado = request.data.get('estado')
        motivo = request.data.get('motivo', '')
        
        if nuevo_estado not in dict(Contrato.ESTADO_CONTRATO_CHOICES):
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estado_anterior = contrato.estado
        contrato.estado = nuevo_estado
        contrato.save()
        
        # Registrar cambio de estado
        EstadoContrato.objects.create(
            contrato=contrato,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            motivo=motivo,
            cambiado_por=request.user
        )
        
        return Response({'message': f'Estado cambiado a {nuevo_estado}'})

    @action(detail=True, methods=['get'])
    def pagos(self, request, pk=None):
        """Obtener pagos del contrato"""
        contrato = self.get_object()
        pagos = PagoContrato.objects.filter(contrato=contrato)
        serializer = PagoContratoSerializer(pagos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def registrar_pago(self, request, pk=None):
        """Registrar nuevo pago para el contrato"""
        contrato = self.get_object()
        data = request.data.copy()
        data['contrato'] = contrato.id
        data['registrado_por'] = request.user.id
        
        serializer = PagoContratoSerializer(data=data)
        if serializer.is_valid():
            pago = serializer.save()
            
            # Actualizar adelanto del contrato
            total_pagos = PagoContrato.objects.filter(contrato=contrato).aggregate(
                total=Sum('monto')
            )['total'] or 0
            
            contrato.adelanto = total_pagos
            contrato.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def clausulas(self, request, pk=None):
        """Obtener cláusulas del contrato"""
        contrato = self.get_object()
        clausulas = ClausulaContrato.objects.filter(contrato=contrato)
        serializer = ClausulaContratoSerializer(clausulas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def agregar_clausula(self, request, pk=None):
        """Agregar nueva cláusula al contrato"""
        contrato = self.get_object()
        data = request.data.copy()
        data['contrato'] = contrato.id
        
        serializer = ClausulaContratoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def historial_estados(self, request, pk=None):
        """Obtener historial de cambios de estado"""
        contrato = self.get_object()
        historial = EstadoContrato.objects.filter(contrato=contrato)
        serializer = EstadoContratoSerializer(historial, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        """Generar PDF del contrato"""
        from .services import ContractPDFService, PDFNotImplemented
        
        contrato = self.get_object()
        
        try:
            return ContractPDFService.generate_response(contrato)
        except PDFNotImplemented:
            return Response(
                {'error': 'Servicio de PDF no disponible. Contacte al administrador.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def exportar_excel(self, request):
        """Exportar contratos a Excel"""
        from .services import ContractExcelService
        
        # Obtener contratos filtrados
        queryset = self.filter_queryset(self.get_queryset())
        
        # Aplicar filtros adicionales si se proporcionan
        filters = request.data.get('filters', {})
        if filters:
            if 'estado' in filters:
                queryset = queryset.filter(estado=filters['estado'])
            if 'tipo_servicio' in filters:
                queryset = queryset.filter(tipo_servicio=filters['tipo_servicio'])
            if 'fecha_desde' in filters:
                queryset = queryset.filter(fecha_inicio__gte=filters['fecha_desde'])
            if 'fecha_hasta' in filters:
                queryset = queryset.filter(fecha_fin__lte=filters['fecha_hasta'])
        
        try:
            excel_file = ContractExcelService.generate_contracts_report(
                queryset, request.user.tenant
            )
            
            filename = f"contratos_{request.user.tenant.slug}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            response = Response(
                excel_file.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except ImportError:
            return Response(
                {'error': 'Servicio de Excel no disponible. Contacte al administrador.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            return Response(
                {'error': f'Error generando Excel: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def exportar_pagos_excel(self, request):
        """Exportar reporte de pagos a Excel"""
        from .services import ContractExcelService
        
        # Obtener contratos con pagos
        queryset = self.filter_queryset(self.get_queryset()).prefetch_related('pagos')
        
        try:
            excel_file = ContractExcelService.generate_payments_report(
                queryset, request.user.tenant
            )
            
            filename = f"pagos_contratos_{request.user.tenant.slug}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            response = Response(
                excel_file.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except ImportError:
            return Response(
                {'error': 'Servicio de Excel no disponible. Contacte al administrador.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            return Response(
                {'error': f'Error generando reporte de pagos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def generar_numero_contrato(self, request, pk=None):
        """Generar número de contrato automático"""
        from .services import ContractDocumentService
        
        numero_contrato = ContractDocumentService.generate_contract_number(request.user.tenant)
        
        return Response({
            'numero_contrato': numero_contrato
        })

    @action(detail=True, methods=['post'])
    def crear_clausulas_defecto(self, request, pk=None):
        """Crear cláusulas por defecto para el contrato"""
        from .services import ContractDocumentService
        
        contrato = self.get_object()
        
        # Verificar que no tenga cláusulas ya
        if contrato.clausulas.exists():
            return Response(
                {'error': 'El contrato ya tiene cláusulas definidas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ContractDocumentService.create_default_clauses(contrato)
            
            # Retornar las cláusulas creadas
            clausulas = ClausulaContrato.objects.filter(contrato=contrato)
            serializer = ClausulaContratoSerializer(clausulas, many=True)
            
            return Response({
                'message': 'Cláusulas por defecto creadas exitosamente',
                'clausulas': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error creando cláusulas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClausulaContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de cláusulas de contratos
    """
    serializer_class = ClausulaContratoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contrato']
    ordering = ['numero_clausula']

    def get_queryset(self):
        """Filtrar cláusulas por tenant del usuario"""
        if self.request.user.is_superuser:
            return ClausulaContrato.objects.all()
        return ClausulaContrato.objects.filter(contrato__tenant=self.request.user.tenant)


class PagoContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pagos de contratos
    """
    serializer_class = PagoContratoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato', 'metodo_pago']
    search_fields = ['numero_operacion', 'observaciones']
    ordering = ['-fecha_pago']

    def get_queryset(self):
        """Filtrar pagos por tenant del usuario"""
        if self.request.user.is_superuser:
            return PagoContrato.objects.all()
        return PagoContrato.objects.filter(contrato__tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        """Asignar usuario automáticamente al crear"""
        serializer.save(registrado_por=self.request.user)


class EstadoContratoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta del historial de estados
    """
    serializer_class = EstadoContratoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contrato', 'estado_nuevo']
    ordering = ['-fecha_cambio']

    def get_queryset(self):
        """Filtrar historial por tenant del usuario"""
        if self.request.user.is_superuser:
            return EstadoContrato.objects.all()
        return EstadoContrato.objects.filter(contrato__tenant=self.request.user.tenant)