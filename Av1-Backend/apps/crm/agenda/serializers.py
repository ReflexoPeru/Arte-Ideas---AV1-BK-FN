from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Evento, Cita, Recordatorio


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class EventoSerializer(serializers.ModelSerializer):
    creado_por = UserSerializer(read_only=True)
    asignado_a = UserSerializer(read_only=True)
    duracion_minutos = serializers.ReadOnlyField()
    esta_vencido = serializers.ReadOnlyField()

    creado_por_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='creado_por', write_only=True)
    asignado_a_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='asignado_a', write_only=True)
    cliente_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'descripcion', 'tipo_evento', 'fecha_inicio', 'fecha_fin',
            'prioridad', 'estado', 'ubicacion', 'enlace_reunion', 'creado_por', 'asignado_a',
            'creado_por_id', 'asignado_a_id', 'cliente_id', 'es_todo_el_dia',
            'recordatorio_minutos', 'notas_internas', 'duracion_minutos', 'esta_vencido',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, data):
        if data.get('fecha_fin') and data.get('fecha_inicio'):
            if data['fecha_fin'] <= data['fecha_inicio']:
                raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
        return data

    def create(self, validated_data):
        cliente_id = validated_data.pop('cliente_id', None)
        if cliente_id:
            from apps.crm.clientes.models import Cliente
            try:
                cliente = Cliente.objects.get(id=cliente_id)
                validated_data['cliente'] = cliente
            except Cliente.DoesNotExist:
                raise serializers.ValidationError(f"Cliente con ID {cliente_id} no existe")
        return Evento.objects.create(**validated_data)


class EventoListSerializer(serializers.ModelSerializer):
    creado_por = UserSerializer(read_only=True)
    asignado_a = UserSerializer(read_only=True)
    duracion_minutos = serializers.ReadOnlyField()
    esta_vencido = serializers.ReadOnlyField()

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'tipo_evento', 'fecha_inicio', 'fecha_fin',
            'prioridad', 'estado', 'creado_por', 'asignado_a', 'duracion_minutos', 'esta_vencido', 'ubicacion'
        ]


class CitaSerializer(serializers.ModelSerializer):
    evento = EventoSerializer(read_only=True)
    evento_id = serializers.PrimaryKeyRelatedField(queryset=Evento.objects.all(), source='evento', write_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    es_cita_hoy = serializers.ReadOnlyField()
    puede_confirmarse = serializers.ReadOnlyField()

    class Meta:
        model = Cita
        fields = [
            'evento', 'evento_id', 'motivo', 'estado_cita', 'cliente', 'cliente_nombre',
            'contacto_cliente', 'telefono_contacto', 'resultado', 'proxima_accion', 'fecha_proxima_accion',
            'valor_oportunidad', 'probabilidad_cierre', 'recordatorio_enviado', 'confirmacion_enviada',
            'es_cita_hoy', 'puede_confirmarse', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class CitaListSerializer(serializers.ModelSerializer):
    evento = EventoListSerializer(read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    es_cita_hoy = serializers.ReadOnlyField()

    class Meta:
        model = Cita
        fields = [
            'evento', 'motivo', 'estado_cita', 'cliente_nombre',
            'es_cita_hoy', 'valor_oportunidad', 'probabilidad_cierre'
        ]


class RecordatorioSerializer(serializers.ModelSerializer):
    evento_titulo = serializers.CharField(source='evento.titulo', read_only=True)
    destinatario_nombre = serializers.CharField(source='destinatario.get_full_name', read_only=True)
    debe_enviarse = serializers.ReadOnlyField()

    class Meta:
        model = Recordatorio
        fields = [
            'id', 'evento', 'evento_titulo', 'tipo_recordatorio', 'minutos_antes', 'enviado', 'fecha_envio',
            'destinatario', 'destinatario_nombre', 'mensaje', 'debe_enviarse', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_envio', 'fecha_creacion']


class AgendaDashboardSerializer(serializers.Serializer):
    total_eventos = serializers.IntegerField()
    eventos_hoy = serializers.IntegerField()
    eventos_proximos = serializers.IntegerField()
    eventos_vencidos = serializers.IntegerField()
    citas_hoy = serializers.IntegerField()
    citas_pendientes = serializers.IntegerField()
    citas_completadas_semana = serializers.IntegerField()
    proximos_eventos = EventoListSerializer(many=True)
    citas_hoy_list = CitaListSerializer(many=True)


class ProximosEventosDemoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField()
    fecha = serializers.DateField()
    hora = serializers.TimeField()
    tipo = serializers.CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        from datetime import datetime
        fecha_str = data['fecha']
        hora_str = data['hora']
        fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        data['fecha_hora_completa'] = fecha_hora.isoformat()
        data['fecha_formateada'] = fecha_hora.strftime("%d/%m/%Y")
        data['hora_formateada'] = fecha_hora.strftime("%H:%M")
        data['dia_semana'] = fecha_hora.strftime("%A").capitalize()
        colores = {
            'Sesión Fotográfica': '#4CAF50',
            'Entrega': '#FF9800',
            'Recordatorio': '#2196F3'
        }
        data['color'] = colores.get(data['tipo'], '#9E9E9E')
        return data


class DisponibilidadSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField()
    hora_fin = serializers.TimeField()
    usuario_id = serializers.IntegerField()

    def validate(self, data):
        if data['hora_fin'] <= data['hora_inicio']:
            raise serializers.ValidationError("La hora fin debe ser posterior a la hora inicio")
        return data