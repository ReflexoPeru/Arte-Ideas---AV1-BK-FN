from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Evento, Cita, Recordatorio


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_evento', 'fecha_inicio', 'fecha_fin', 'prioridad', 'estado', 'asignado_a', 'cliente_link']
    list_filter = ['tipo_evento', 'prioridad', 'estado', 'es_todo_el_dia', 'fecha_inicio', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion', 'ubicacion', 'cliente__nombres', 'cliente__apellidos']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'duracion_display', 'esta_vencido_display']

    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo_evento', 'prioridad', 'estado')
        }),
        ('Fechas y Horarios', {
            'fields': ('fecha_inicio', 'fecha_fin', 'es_todo_el_dia', 'recordatorio_minutos', 'duracion_display')
        }),
        ('Ubicación y Enlaces', {
            'fields': ('ubicacion', 'enlace_reunion')
        }),
        ('Asignaciones', {
            'fields': ('creado_por', 'asignado_a', 'cliente')
        }),
        ('Información Adicional', {
            'fields': ('notas_internas', 'esta_vencido_display')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def duracion_display(self, obj):
        """Mostrar duración de forma legible"""
        if obj.duracion_minutos is None:
            return "No disponible (fechas no definidas)"
        horas = obj.duracion_minutos // 60
        minutos = obj.duracion_minutos % 60
        if horas > 0:
            return f"{horas}h {minutos}m ({obj.duracion_minutos} minutos)"
        return f"{minutos}m ({obj.duracion_minutos} minutos)"
    duracion_display.short_description = 'Duración'

    def esta_vencido_display(self, obj):
        """Mostrar estado de vencimiento de forma legible"""
        if obj.fecha_fin is None:
            return "No disponible (fecha de fin no definida)"
        if obj.esta_vencido:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Vencido</span>')
        return format_html('<span style="color: green;">✓ Activo</span>')
    esta_vencido_display.short_description = 'Estado'

    def get_readonly_fields(self, request, obj=None):
        """Hacer campos readonly según el contexto"""
        readonly = list(super().get_readonly_fields(request, obj))
        # Si es un nuevo objeto, no hacer readonly los campos de fecha
        # ya que necesitan ser editables durante la creación
        return readonly

    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el usuario creador y asignado si no se especificaron"""
        if not change:  # Solo al crear
            if not obj.creado_por_id:
                obj.creado_por = request.user
            if not obj.asignado_a_id:
                obj.asignado_a = request.user
        super().save_model(request, obj, form, change)

    def cliente_link(self, obj):
        if obj.cliente:
            url = reverse('admin:clientes_cliente_change', args=[obj.cliente.id])
            return format_html('<a href="{}">{}</a>', url, obj.cliente.obtener_nombre_completo())
        return "-"
    cliente_link.short_description = 'Cliente'


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['evento', 'cliente', 'motivo', 'estado_cita', 'valor_oportunidad', 'probabilidad_cierre']
    list_filter = ['motivo', 'estado_cita', 'evento__fecha_inicio', 'recordatorio_enviado', 'confirmacion_enviada']
    search_fields = ['evento__titulo', 'cliente__nombres', 'cliente__apellidos', 'contacto_cliente', 'resultado']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ['evento', 'tipo_recordatorio', 'minutos_antes', 'enviado', 'destinatario']
    list_filter = ['tipo_recordatorio', 'enviado', 'fecha_creacion', 'fecha_envio']
    search_fields = ['evento__titulo', 'mensaje', 'destinatario__username']