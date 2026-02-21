from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render
from datetime import datetime, timedelta

from .models import Evento, Cita, Recordatorio
from .serializers import (
    EventoSerializer, EventoListSerializer,
    CitaSerializer, CitaListSerializer,
    RecordatorioSerializer, AgendaDashboardSerializer,
    ProximosEventosDemoSerializer, DisponibilidadSerializer
)
from .filters import EventoFilter, CitaFilter


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventoFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return EventoListSerializer
        return EventoSerializer

    def get_queryset(self):
        queryset = Evento.objects.select_related('creado_por', 'asignado_a', 'cliente')
        if not self.request.user.is_staff:
            queryset = queryset.filter(Q(creado_por=self.request.user) | Q(asignado_a=self.request.user))
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        usuario_id = self.request.query_params.get('usuario_id')
        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_fin__date__lte=fecha_fin)
        if usuario_id:
            queryset = queryset.filter(asignado_a_id=usuario_id)
        return queryset.order_by('fecha_inicio')

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def proximos_eventos(self, request):
        hoy = timezone.now().date()
        proximos_dias = hoy + timedelta(days=30)
        queryset = self.get_queryset().filter(fecha_inicio__date__gte=hoy, fecha_inicio__date__lte=proximos_dias)[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def eventos_hoy(self, request):
        hoy = timezone.now().date()
        queryset = self.get_queryset().filter(fecha_inicio__date=hoy)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def eventos_semana(self, request):
        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        queryset = self.get_queryset().filter(fecha_inicio__date__range=[inicio_semana, fin_semana])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def verificar_disponibilidad(self, request):
        serializer = DisponibilidadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        fecha = datos['fecha']
        hora_inicio = datos['hora_inicio']
        hora_fin = datos['hora_fin']
        usuario_id = datos['usuario_id']
        fecha_hora_inicio = datetime.combine(fecha, hora_inicio)
        fecha_hora_fin = datetime.combine(fecha, hora_fin)
        eventos_existentes = Evento.objects.filter(
            asignado_a_id=usuario_id,
            fecha_inicio__lt=fecha_hora_fin,
            fecha_fin__gt=fecha_hora_inicio
        )
        disponible = not eventos_existentes.exists()
        return Response({
            'disponible': disponible,
            'eventos_conflicto': EventoListSerializer(eventos_existentes, many=True).data if eventos_existentes else []
        })

    @action(detail=True, methods=['post'])
    def completar_evento(self, request, pk=None):
        evento = self.get_object()
        if evento.estado == 'completado':
            return Response({'error': 'El evento ya está completado'}, status=status.HTTP_400_BAD_REQUEST)
        evento.estado = 'completado'
        evento.save()
        serializer = self.get_serializer(evento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar_evento(self, request, pk=None):
        evento = self.get_object()
        if evento.estado == 'cancelado':
            return Response({'error': 'El evento ya está cancelado'}, status=status.HTTP_400_BAD_REQUEST)
        motivo = request.data.get('motivo', '')
        evento.estado = 'cancelado'
        evento.notas_internas = f"{evento.notas_internas or ''}\nCancelado: {motivo}"
        evento.save()
        serializer = self.get_serializer(evento)
        return Response(serializer.data)


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CitaFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return CitaListSerializer
        return CitaSerializer

    def get_queryset(self):
        queryset = Cita.objects.select_related('evento', 'cliente').filter(evento__asignado_a=self.request.user)
        estado = self.request.query_params.get('estado')
        fecha = self.request.query_params.get('fecha')
        cliente_id = self.request.query_params.get('cliente_id')
        if estado:
            queryset = queryset.filter(estado_cita=estado)
        if fecha:
            queryset = queryset.filter(evento__fecha_inicio__date=fecha)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        return queryset.order_by('evento__fecha_inicio')

    @action(detail=False, methods=['get'])
    def citas_hoy(self, request):
        hoy = timezone.now().date()
        queryset = self.get_queryset().filter(evento__fecha_inicio__date=hoy)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def citas_semana(self, request):
        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        queryset = self.get_queryset().filter(evento__fecha_inicio__date__range=[inicio_semana, fin_semana])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirmar_cita(self, request, pk=None):
        cita = self.get_object()
        if cita.estado_cita != 'programada':
            return Response({'error': 'Solo se pueden confirmar citas programadas'}, status=status.HTTP_400_BAD_REQUEST)
        cita.estado_cita = 'confirmada'
        cita.confirmacion_enviada = True
        cita.save()
        serializer = self.get_serializer(cita)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def completar_cita(self, request, pk=None):
        cita = self.get_object()
        if cita.estado_cita not in ['programada', 'confirmada', 'en_curso']:
            return Response({'error': 'No se puede completar una cita en este estado'}, status=status.HTTP_400_BAD_REQUEST)
        resultado = request.data.get('resultado', '')
        proxima_accion = request.data.get('proxima_accion', '')
        fecha_proxima_accion = request.data.get('fecha_proxima_accion')
        cita.resultado = resultado
        cita.proxima_accion = proxima_accion
        cita.fecha_proxima_accion = fecha_proxima_accion
        cita.estado_cita = 'completada'
        cita.save()
        cita.evento.estado = 'completado'
        cita.evento.save()
        serializer = self.get_serializer(cita)
        return Response(serializer.data)


class RecordatorioViewSet(viewsets.ModelViewSet):
    queryset = Recordatorio.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RecordatorioSerializer

    def get_queryset(self):
        return Recordatorio.objects.filter(destinatario=self.request.user).select_related('evento', 'destinatario')

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        queryset = self.get_queryset().filter(enviado=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_enviado(self, request, pk=None):
        recordatorio = self.get_object()
        recordatorio.enviado = True
        recordatorio.fecha_envio = timezone.now()
        recordatorio.save()
        serializer = self.get_serializer(recordatorio)
        return Response(serializer.data)


class AgendaDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        hoy = timezone.now().date()
        semana_pasada = hoy - timedelta(days=7)
        proximos_dias = hoy + timedelta(days=30)
        total_eventos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user)).count()
        eventos_hoy = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_inicio__date=hoy).count()
        eventos_proximos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_inicio__date__gt=hoy, fecha_inicio__date__lte=proximos_dias).count()
        eventos_vencidos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_fin__lt=timezone.now(), estado__in=['pendiente', 'en_progreso']).count()
        citas_hoy = Cita.objects.filter(evento__asignado_a=user, evento__fecha_inicio__date=hoy).count()
        citas_pendientes = Cita.objects.filter(evento__asignado_a=user, estado_cita__in=['programada', 'confirmada']).count()
        citas_completadas_semana = Cita.objects.filter(evento__asignado_a=user, estado_cita='completada', evento__fecha_inicio__date__gte=semana_pasada).count()
        proximos_eventos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_inicio__date__gte=hoy).order_by('fecha_inicio')[:5]
        citas_hoy_list = Cita.objects.filter(evento__asignado_a=user, evento__fecha_inicio__date=hoy).order_by('evento__fecha_inicio')
        data = {
            'total_eventos': total_eventos,
            'eventos_hoy': eventos_hoy,
            'eventos_proximos': eventos_proximos,
            'eventos_vencidos': eventos_vencidos,
            'citas_hoy': citas_hoy,
            'citas_pendientes': citas_pendientes,
            'citas_completadas_semana': citas_completadas_semana,
            'proximos_eventos': EventoListSerializer(proximos_eventos, many=True).data,
            'citas_hoy_list': CitaListSerializer(citas_hoy_list, many=True).data,
        }
        serializer = AgendaDashboardSerializer(data)
        return Response(serializer.data)


class AgendaDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        hoy = timezone.now().date()
        semana_pasada = hoy - timedelta(days=7)
        proximos_dias = hoy + timedelta(days=30)
        total_eventos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user)).count()
        eventos_hoy = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_inicio__date=hoy).count()
        eventos_proximos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_inicio__date__gt=hoy, fecha_inicio__date__lte=proximos_dias).count()
        eventos_vencidos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_fin__lt=timezone.now(), estado__in=['pendiente', 'en_progreso']).count()
        citas_hoy = Cita.objects.filter(evento__asignado_a=user, evento__fecha_inicio__date=hoy).count()
        citas_pendientes = Cita.objects.filter(evento__asignado_a=user, estado_cita__in=['programada', 'confirmada']).count()
        citas_completadas_semana = Cita.objects.filter(evento__asignado_a=user, estado_cita='completada', evento__fecha_inicio__date__gte=semana_pasada).count()
        proximos_eventos = Evento.objects.filter(Q(creado_por=user) | Q(asignado_a=user), fecha_inicio__date__gte=hoy).order_by('fecha_inicio')[:5]
        citas_hoy_list = Cita.objects.filter(evento__asignado_a=user, evento__fecha_inicio__date=hoy).order_by('evento__fecha_inicio')
        data = {
            'total_eventos': total_eventos,
            'eventos_hoy': eventos_hoy,
            'eventos_proximos': eventos_proximos,
            'eventos_vencidos': eventos_vencidos,
            'citas_hoy': citas_hoy,
            'citas_pendientes': citas_pendientes,
            'citas_completadas_semana': citas_completadas_semana,
            'proximos_eventos': EventoListSerializer(proximos_eventos, many=True).data,
            'citas_hoy_list': CitaListSerializer(citas_hoy_list, many=True).data,
        }
        serializer = AgendaDashboardSerializer(data)
        return Response(serializer.data)


class ProximosEventosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoy = timezone.now().date()
        proximos_dias = hoy + timedelta(days=30)
        queryset = Evento.objects.filter(Q(creado_por=request.user) | Q(asignado_a=request.user), fecha_inicio__date__gte=hoy, fecha_inicio__date__lte=proximos_dias).order_by('fecha_inicio')[:10]
        serializer = EventoListSerializer(queryset, many=True)
        return Response(serializer.data)


class EventosHoyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoy = timezone.now().date()
        queryset = Evento.objects.filter(Q(creado_por=request.user) | Q(asignado_a=request.user), fecha_inicio__date=hoy).order_by('fecha_inicio')
        serializer = EventoListSerializer(queryset, many=True)
        return Response(serializer.data)


class CitasPendientesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Cita.objects.filter(evento__asignado_a=request.user, estado_cita__in=['programada', 'confirmada']).order_by('evento__fecha_inicio')
        serializer = CitaListSerializer(queryset, many=True)
        return Response(serializer.data)


class ProximosEventosDemoView(APIView):
    permission_classes = []

    def get(self, request):
        eventos_demo = [
            {"id": 1, "titulo": "Colegio San José", "fecha": "2025-11-02", "hora": "10:00", "tipo": "Sesión Fotográfica"},
            {"id": 2, "titulo": "Roberto Silva", "fecha": "2025-11-03", "hora": "11:30", "tipo": "Sesión Fotográfica"},
            {"id": 3, "titulo": "Carlos Mendoza", "fecha": "2025-11-07", "hora": "16:30", "tipo": "Entrega"},
        ]
        from datetime import datetime, date as date_cls
        hoy = date_cls.today()
        eventos_futuros = [e for e in eventos_demo if datetime.strptime(e['fecha'], "%Y-%m-%d").date() >= hoy]
        eventos_futuros.sort(key=lambda x: (x['fecha'], x['hora']))
        eventos_limitados = eventos_futuros[:15]
        serializer = ProximosEventosDemoSerializer(eventos_limitados, many=True)
        return Response({
            'total_eventos': len(eventos_futuros),
            'eventos': serializer.data,
            'fecha_actual': hoy.isoformat()
        })


def demo_proximos_eventos(request):
    return render(request, 'agenda/proximos_eventos_demo.html')