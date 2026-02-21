"""
Modelos de Agenda - Arte Ideas CRM
Gestión de eventos, citas y recordatorios
"""
from django.db import models
from django.conf import settings


class Evento(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('reunion', 'Reunión'),
        ('llamada', 'Llamada'),
        ('visita', 'Visita'),
        ('tarea', 'Tarea'),
        ('recordatorio', 'Recordatorio'),
        ('otro', 'Otro'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('pospuesto', 'Pospuesto'),
    ]

    titulo = models.CharField(max_length=200, verbose_name='Título del Evento')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, default='reunion', verbose_name='Tipo de Evento')
    fecha_inicio = models.DateTimeField(verbose_name='Fecha y Hora de Inicio')
    fecha_fin = models.DateTimeField(verbose_name='Fecha y Hora de Fin')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media', verbose_name='Prioridad')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    ubicacion = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ubicación')
    enlace_reunion = models.URLField(blank=True, null=True, verbose_name='Enlace de Reunión')
    es_todo_el_dia = models.BooleanField(default=False, verbose_name='Todo el Día')
    recordatorio_minutos = models.IntegerField(default=15, verbose_name='Recordatorio (minutos antes)')
    notas_internas = models.TextField(blank=True, null=True, verbose_name='Notas Internas')

    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='eventos_creados', verbose_name='Creado Por')
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='eventos_asignados', verbose_name='Asignado A')

    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Cliente')

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['fecha_inicio', 'prioridad']
        indexes = [
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
            models.Index(fields=['asignado_a', 'estado']),
            models.Index(fields=['tipo_evento', 'prioridad']),
        ]

    def __str__(self):
        if self.fecha_inicio:
            return f"{self.titulo} - {self.fecha_inicio}"
        return self.titulo

    @property
    def duracion_minutos(self):
        """Calcular duración en minutos. Retorna None si las fechas no están definidas."""
        if self.fecha_inicio is None or self.fecha_fin is None:
            return None
        return int((self.fecha_fin - self.fecha_inicio).total_seconds() // 60)

    @property
    def esta_vencido(self):
        """Verificar si el evento está vencido. Retorna False si las fechas no están definidas."""
        if self.fecha_fin is None:
            return False
        from django.utils import timezone
        return self.estado in ['pendiente', 'en_progreso'] and self.fecha_fin < timezone.now()

    @property
    def tiempo_restante(self):
        """Calcular tiempo restante hasta el evento. Retorna None si la fecha no está definida."""
        if self.fecha_inicio is None:
            return None
        from django.utils import timezone
        delta = self.fecha_inicio - timezone.now()
        return delta.total_seconds()


class Cita(models.Model):
    MOTIVO_CHOICES = [
        ('presentacion', 'Presentación de Productos'),
        ('seguimiento', 'Seguimiento'),
        ('cierre_venta', 'Cierre de Venta'),
        ('soporte', 'Soporte Técnico'),
        ('reunion_negocios', 'Reunión de Negocios'),
        ('visita_inspeccion', 'Visita de Inspección'),
        ('otro', 'Otro'),
    ]

    ESTADO_CITA_CHOICES = [
        ('programada', 'Programada'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió'),
    ]

    evento = models.OneToOneField(Evento, on_delete=models.CASCADE, primary_key=True, verbose_name='Evento')
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES, default='seguimiento', verbose_name='Motivo de la Cita')
    estado_cita = models.CharField(max_length=15, choices=ESTADO_CITA_CHOICES, default='programada', verbose_name='Estado de la Cita')
    contacto_cliente = models.CharField(max_length=200, blank=True, null=True, verbose_name='Persona de Contacto')
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono de Contacto')
    resultado = models.TextField(blank=True, null=True, verbose_name='Resultado de la Cita')
    proxima_accion = models.TextField(blank=True, null=True, verbose_name='Próxima Acción')
    fecha_proxima_accion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Próxima Acción')
    valor_oportunidad = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Valor de la Oportunidad')
    probabilidad_cierre = models.IntegerField(default=50, verbose_name='Probabilidad de Cierre (%)')
    recordatorio_enviado = models.BooleanField(default=False, verbose_name='Recordatorio Enviado')
    confirmacion_enviada = models.BooleanField(default=False, verbose_name='Confirmación Enviada')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, verbose_name='Cliente')

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['evento__fecha_inicio']

    def __str__(self):
        if hasattr(self, 'evento') and self.evento:
            return f"Cita: {self.evento.titulo} ({self.get_estado_cita_display()})"
        return f"Cita ({self.get_estado_cita_display()})"

    @property
    def es_cita_hoy(self):
        if not hasattr(self, 'evento') or not self.evento or not self.evento.fecha_inicio:
            return False
        from django.utils import timezone
        return self.evento.fecha_inicio.date() == timezone.now().date()

    @property
    def puede_confirmarse(self):
        return self.estado_cita == 'programada'


class Recordatorio(models.Model):
    TIPO_RECORDATORIO_CHOICES = [
        ('email', 'Correo Electrónico'),
        ('notificacion', 'Notificación Push'),
        ('sms', 'SMS'),
        ('sistema', 'Notificación del Sistema'),
    ]

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='recordatorios', verbose_name='Evento')
    tipo_recordatorio = models.CharField(max_length=15, choices=TIPO_RECORDATORIO_CHOICES, default='sistema', verbose_name='Tipo de Recordatorio')
    minutos_antes = models.IntegerField(default=15, verbose_name='Minutos Antes del Evento')
    enviado = models.BooleanField(default=False, verbose_name='Enviado')
    fecha_envio = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Envío')
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Destinatario')
    mensaje = models.TextField(verbose_name='Mensaje del Recordatorio')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        ordering = ['fecha_creacion']

    def __str__(self):
        if hasattr(self, 'evento') and self.evento:
            return f"Recordatorio: {self.evento.titulo} -> {self.destinatario}"
        return f"Recordatorio -> {self.destinatario}"

    @property
    def debe_enviarse(self):
        from django.utils import timezone
        if self.enviado or not hasattr(self, 'evento') or self.evento is None or self.evento.fecha_inicio is None:
            return False
        envio_programado = self.evento.fecha_inicio - timezone.timedelta(minutes=self.minutos_antes)
        return timezone.now() >= envio_programado