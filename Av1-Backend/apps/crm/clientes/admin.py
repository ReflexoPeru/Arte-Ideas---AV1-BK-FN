"""
Admin del Módulo de Clientes - Arte Ideas CRM
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Cliente, HistorialCliente, ContactoCliente


class ContactoClienteInline(admin.TabularInline):
    """Inline para contactos adicionales del cliente"""
    model = ContactoCliente
    extra = 1
    fields = ['nombre', 'cargo', 'telefono', 'email', 'es_principal']


class HistorialClienteInline(admin.TabularInline):
    """Inline para historial del cliente"""
    model = HistorialCliente
    extra = 0
    readonly_fields = ['fecha', 'registrado_por', 'creado_en']
    fields = ['tipo_interaccion', 'fecha', 'descripcion', 'resultado', 'registrado_por']
    ordering = ['-fecha']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Admin para gestión de clientes"""
    list_display = [
        'nombre_completo_display', 'tipo_cliente_indicator', 'email', 'telefono', 
        'dni', 'info_adicional', 'activo_indicator', 'creado_en_formateado'
    ]
    list_filter = ['tipo_cliente', 'activo', 'nivel_educativo', 'creado_en']
    search_fields = [
        'nombres', 'apellidos', 'email', 'telefono', 'dni',
        'razon_social', 'grado', 'seccion'
    ]
    ordering = ['-creado_en']
    # inlines = [ContactoClienteInline, HistorialClienteInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tipo_cliente', 'nombres', 'apellidos', 'email', 'telefono', 'dni', 'direccion')
        }),
        ('Información de Empresa', {
            'fields': ('razon_social',),
            'classes': ('collapse',),
            'description': 'Solo para clientes tipo Empresa'
        }),
        ('Información de Colegio', {
            'fields': ('nivel_educativo', 'grado', 'seccion'),
            'classes': ('collapse',),
            'description': 'Solo para clientes tipo Colegio'
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',),
            'description': 'Información de auditoría'
        })
    )
    
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def nombre_completo_display(self, obj):
        """Mostrar nombre completo con icono según tipo"""
        icons = {
            'particular': '👤',
            'empresa': '🏢',
            'colegio': '🏫'
        }
        icon = icons.get(obj.tipo_cliente, '❓')
        return f"{icon} {obj.obtener_nombre_completo()}"
    nombre_completo_display.short_description = 'Cliente'
    nombre_completo_display.admin_order_field = 'nombres'
    
    def tipo_cliente_indicator(self, obj):
        """Indicador visual del tipo de cliente"""
        colors = {
            'particular': 'blue',
            'empresa': 'green',
            'colegio': 'purple'
        }
        color = colors.get(obj.tipo_cliente, 'gray')
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">● {obj.get_tipo_cliente_display()}</span>')
    tipo_cliente_indicator.short_description = 'Tipo'
    
    def info_adicional(self, obj):
        """Información adicional según tipo de cliente"""
        if obj.tipo_cliente == 'empresa' and obj.razon_social:
            return mark_safe(f'<small style="color: green;">{obj.razon_social}</small>')
        elif obj.tipo_cliente == 'colegio':
            info = []
            if obj.nivel_educativo:
                info.append(obj.get_nivel_educativo_display())
            if obj.grado:
                info.append(f"Grado: {obj.grado}")
            if obj.seccion:
                info.append(f"Sección: {obj.seccion}")
            return mark_safe(f'<small style="color: purple;">{" | ".join(info)}</small>')
        return '-'
    info_adicional.short_description = 'Info Adicional'
    
    def activo_indicator(self, obj):
        """Indicador de estado activo/inactivo"""
        if obj.activo:
            return mark_safe('<span style="color: green; font-weight: bold;">✅ Activo</span>')
        return mark_safe('<span style="color: red; font-weight: bold;">❌ Inactivo</span>')
    activo_indicator.short_description = 'Estado'
    
    def creado_en_formateado(self, obj):
        """Fecha de creación formateada"""
        return obj.creado_en.strftime('%d/%m/%Y %H:%M')
    creado_en_formateado.short_description = 'Creado'
    creado_en_formateado.admin_order_field = 'creado_en'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
        return qs.none()
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar formulario según el usuario"""
        form = super().get_form(request, obj, **kwargs)
        # Para usuarios no superusuarios, excluir el campo tenant del formulario
        # (los superusuarios pueden verlo y seleccionarlo)
        if not request.user.is_superuser and 'tenant' in form.base_fields:
            del form.base_fields['tenant']
        return form
    
    def get_fieldsets(self, request, obj=None):
        """Mostrar campo tenant solo a superusuarios"""
        fieldsets = super().get_fieldsets(request, obj)
        
        # Si es superusuario, agregar campo tenant al inicio
        if request.user.is_superuser:
            # Convertir fieldsets a lista mutable
            fieldsets_list = []
            for name, options in fieldsets:
                if name == 'Información Básica':
                    # Agregar tenant al principio de este fieldset
                    fields = list(options.get('fields', ()))
                    if 'tenant' not in fields:
                        fields.insert(0, 'tenant')
                    options = dict(options)
                    options['fields'] = tuple(fields)
                fieldsets_list.append((name, options))
            return tuple(fieldsets_list)
        
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el tenant del usuario"""
        # Si no es superusuario, asignar automáticamente el tenant del usuario
        if not request.user.is_superuser:
            if hasattr(request.user, 'tenant') and request.user.tenant:
                obj.tenant = request.user.tenant
            else:
                # Esto no debería ocurrir debido a has_add_permission, pero por seguridad
                raise ValidationError('No se puede crear un cliente sin un estudio fotográfico asignado.')
        # Si es superusuario y no se seleccionó tenant, intentar usar el del usuario si existe
        elif request.user.is_superuser and not obj.tenant:
            if hasattr(request.user, 'tenant') and request.user.tenant:
                obj.tenant = request.user.tenant
            # Si es superusuario sin tenant, el campo es obligatorio en el formulario
            # Django validará esto antes de llegar aquí
        
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        """Verificar permisos para agregar clientes"""
        # Usuarios sin tenant no pueden crear clientes (a menos que sean superusuarios)
        if not request.user.is_superuser:
            if not (hasattr(request.user, 'tenant') and request.user.tenant):
                return False
        return super().has_add_permission(request)
    
    actions = ['activar_clientes', 'desactivar_clientes', 'exportar_clientes']
    
    def activar_clientes(self, request, queryset):
        """Activar clientes seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} cliente(s) activado(s).', messages.SUCCESS)
    activar_clientes.short_description = "Activar clientes seleccionados"
    
    def desactivar_clientes(self, request, queryset):
        """Desactivar clientes seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} cliente(s) desactivado(s).', messages.WARNING)
    desactivar_clientes.short_description = "Desactivar clientes seleccionados"
    
    def exportar_clientes(self, request, queryset):
        """Exportar clientes seleccionados"""
        count = queryset.count()
        self.message_user(
            request, 
            f'Exportando {count} cliente(s). Función pendiente de implementación.',
            messages.INFO
        )
    exportar_clientes.short_description = "Exportar clientes seleccionados"


@admin.register(HistorialCliente)
class HistorialClienteAdmin(admin.ModelAdmin):
    """Admin para historial de clientes"""
    list_display = [
        'cliente_nombre', 'tipo_interaccion_display', 'fecha_formateada',
        'descripcion_corta', 'registrado_por'
    ]
    list_filter = ['tipo_interaccion', 'fecha', 'registrado_por']
    search_fields = [
        'cliente__nombres', 'cliente__apellidos', 'descripcion', 'resultado'
    ]
    ordering = ['-fecha']
    readonly_fields = ['creado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cliente', 'tipo_interaccion', 'fecha')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'resultado')
        }),
        ('Auditoría', {
            'fields': ('registrado_por', 'creado_en'),
            'classes': ('collapse',)
        })
    )
    
    def cliente_nombre(self, obj):
        """Nombre del cliente"""
        return obj.cliente.obtener_nombre_completo()
    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'cliente__nombres'
    
    def tipo_interaccion_display(self, obj):
        """Tipo de interacción con color"""
        colors = {
            'llamada': 'blue',
            'email': 'green',
            'reunion': 'purple',
            'whatsapp': 'orange',
            'visita': 'red',
            'evento': 'brown',
            'otro': 'gray'
        }
        color = colors.get(obj.tipo_interaccion, 'gray')
        return mark_safe(f'<span style="color: {color};">● {obj.get_tipo_interaccion_display()}</span>')
    tipo_interaccion_display.short_description = 'Tipo'
    
    def fecha_formateada(self, obj):
        """Fecha formateada"""
        return obj.fecha.strftime('%d/%m/%Y %H:%M')
    fecha_formateada.short_description = 'Fecha'
    fecha_formateada.admin_order_field = 'fecha'
    
    def descripcion_corta(self, obj):
        """Descripción truncada"""
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(cliente__tenant=request.user.tenant)
        return qs.none()


@admin.register(ContactoCliente)
class ContactoClienteAdmin(admin.ModelAdmin):
    """Admin para contactos de clientes"""
    list_display = [
        'nombre', 'cliente_nombre', 'cargo', 'telefono', 'email', 'es_principal_display'
    ]
    list_filter = ['es_principal', 'creado_en']
    search_fields = ['nombre', 'cargo', 'telefono', 'email', 'cliente__nombres', 'cliente__apellidos']
    ordering = ['-es_principal', 'nombre']
    
    fieldsets = (
        ('Información del Contacto', {
            'fields': ('cliente', 'nombre', 'cargo', 'es_principal')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'email')
        })
    )
    
    def cliente_nombre(self, obj):
        """Nombre del cliente"""
        return obj.cliente.obtener_nombre_completo()
    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'cliente__nombres'
    
    def es_principal_display(self, obj):
        """Indicador de contacto principal"""
        if obj.es_principal:
            return mark_safe('<span style="color: green; font-weight: bold;">⭐ Principal</span>')
        return mark_safe('<span style="color: gray;">○ Secundario</span>')
    es_principal_display.short_description = 'Tipo'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(cliente__tenant=request.user.tenant)
        return qs.none()