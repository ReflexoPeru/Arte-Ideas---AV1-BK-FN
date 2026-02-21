from django_filters import rest_framework as filters
from .models import Evento, Cita


class EventoFilter(filters.FilterSet):
    fecha_inicio = filters.DateTimeFilter(field_name='fecha_inicio', lookup_expr='gte')
    fecha_fin = filters.DateTimeFilter(field_name='fecha_fin', lookup_expr='lte')
    fecha_exacta = filters.DateFilter(field_name='fecha_inicio', lookup_expr='date')
    fecha_inicio_range = filters.DateFromToRangeFilter(field_name='fecha_inicio', lookup_expr='date')
    fecha_creacion_range = filters.DateFromToRangeFilter(field_name='fecha_creacion', lookup_expr='date')
    tipo_evento = filters.CharFilter(field_name='tipo_evento', lookup_expr='exact')
    prioridad = filters.CharFilter(field_name='prioridad', lookup_expr='exact')
    estado = filters.CharFilter(field_name='estado', lookup_expr='exact')
    creado_por = filters.NumberFilter(field_name='creado_por__id')
    asignado_a = filters.NumberFilter(field_name='asignado_a__id')
    es_todo_el_dia = filters.BooleanFilter(field_name='es_todo_el_dia')
    titulo = filters.CharFilter(field_name='titulo', lookup_expr='icontains')
    descripcion = filters.CharFilter(field_name='descripcion', lookup_expr='icontains')
    ubicacion = filters.CharFilter(field_name='ubicacion', lookup_expr='icontains')
    vencidos = filters.BooleanFilter(method='filter_vencidos', label='Eventos vencidos')
    proximos = filters.BooleanFilter(method='filter_proximos', label='Próximos eventos')
    hoy = filters.BooleanFilter(method='filter_hoy', label='Eventos de hoy')

    class Meta:
        model = Evento
        fields = [
            'fecha_inicio', 'fecha_fin', 'fecha_exacta', 'fecha_inicio_range', 'fecha_creacion_range',
            'tipo_evento', 'prioridad', 'estado', 'creado_por', 'asignado_a', 'es_todo_el_dia',
            'titulo', 'descripcion', 'ubicacion', 'vencidos', 'proximos', 'hoy'
        ]

    def filter_vencidos(self, queryset, name, value):
        if value:
            from django.utils import timezone
            return queryset.filter(fecha_fin__lt=timezone.now(), estado__in=['pendiente', 'en_progreso'])
        return queryset

    def filter_proximos(self, queryset, name, value):
        if value:
            from django.utils import timezone
            from datetime import timedelta
            hoy = timezone.now().date()
            proxima_semana = hoy + timedelta(days=7)
            return queryset.filter(fecha_inicio__date__gte=hoy, fecha_inicio__date__lte=proxima_semana)
        return queryset

    def filter_hoy(self, queryset, name, value):
        if value:
            from django.utils import timezone
            hoy = timezone.now().date()
            return queryset.filter(fecha_inicio__date=hoy)
        return queryset


class CitaFilter(filters.FilterSet):
    fecha = filters.DateFilter(field_name='evento__fecha_inicio', lookup_expr='date')
    fecha_inicio = filters.DateTimeFilter(field_name='evento__fecha_inicio', lookup_expr='gte')
    fecha_fin = filters.DateTimeFilter(field_name='evento__fecha_fin', lookup_expr='lte')
    fecha_range = filters.DateFromToRangeFilter(field_name='evento__fecha_inicio', lookup_expr='date')
    motivo = filters.CharFilter(field_name='motivo', lookup_expr='exact')
    estado_cita = filters.CharFilter(field_name='estado_cita', lookup_expr='exact')
    evento = filters.NumberFilter(field_name='evento__id')
    valor_min = filters.NumberFilter(field_name='valor_oportunidad', lookup_expr='gte')
    valor_max = filters.NumberFilter(field_name='valor_oportunidad', lookup_expr='lte')
    probabilidad_min = filters.NumberFilter(field_name='probabilidad_cierre', lookup_expr='gte')
    probabilidad_max = filters.NumberFilter(field_name='probabilidad_cierre', lookup_expr='lte')
    recordatorio_enviado = filters.BooleanFilter(field_name='recordatorio_enviado')
    confirmacion_enviada = filters.BooleanFilter(field_name='confirmacion_enviada')
    contacto_cliente = filters.CharFilter(field_name='contacto_cliente', lookup_expr='icontains')
    telefono_contacto = filters.CharFilter(field_name='telefono_contacto', lookup_expr='icontains')
    resultado = filters.CharFilter(field_name='resultado', lookup_expr='icontains')
    hoy = filters.BooleanFilter(method='filter_hoy', label='Citas de hoy')
    proximas = filters.BooleanFilter(method='filter_proximas', label='Próximas citas')
    vencidas = filters.BooleanFilter(method='filter_vencidas', label='Citas vencidas')

    class Meta:
        model = Cita
        fields = [
            'fecha', 'fecha_inicio', 'fecha_fin', 'fecha_range', 'motivo', 'estado_cita', 'evento',
            'valor_min', 'valor_max', 'probabilidad_min', 'probabilidad_max', 'recordatorio_enviado',
            'confirmacion_enviada', 'contacto_cliente', 'telefono_contacto', 'resultado', 'hoy', 'proximas', 'vencidas'
        ]

    def filter_hoy(self, queryset, name, value):
        if value:
            from django.utils import timezone
            hoy = timezone.now().date()
            return queryset.filter(evento__fecha_inicio__date=hoy)
        return queryset

    def filter_proximas(self, queryset, name, value):
        if value:
            from django.utils import timezone
            from datetime import timedelta
            hoy = timezone.now().date()
            proxima_semana = hoy + timedelta(days=7)
            return queryset.filter(evento__fecha_inicio__date__gte=hoy, evento__fecha_inicio__date__lte=proxima_semana)
        return queryset

    def filter_vencidas(self, queryset, name, value):
        if value:
            from django.utils import timezone
            return queryset.filter(evento__fecha_inicio__lt=timezone.now(), estado_cita__in=['programada', 'confirmada'])
        return queryset