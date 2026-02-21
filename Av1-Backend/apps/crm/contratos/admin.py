"""
Admin del Módulo de Contratos - Arte Ideas CRM
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
from django import forms
from .models import Contrato, ClausulaContrato, PagoContrato, EstadoContrato
from apps.core.models import Tenant


class ContratoAdminForm(forms.ModelForm):
    """Formulario personalizado para Contrato que siempre incluye el campo tenant"""
    
    class Meta:
        model = Contrato
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que el campo tenant siempre esté presente
        if 'tenant' not in self.fields:
            self.fields['tenant'] = forms.ModelChoiceField(
                queryset=Tenant.objects.all(),
                required=True,
                label='Estudio Fotográfico'
            )


class ClausulaContratoInline(admin.TabularInline):
    """Inline para cláusulas del contrato"""
    model = ClausulaContrato
    extra = 1
    fields = ['numero_clausula', 'titulo', 'contenido']
    ordering = ['numero_clausula']


class PagoContratoInline(admin.TabularInline):
    """Inline para pagos del contrato"""
    model = PagoContrato
    extra = 0
    readonly_fields = ['registrado_por', 'creado_en']
    fields = ['fecha_pago', 'monto', 'metodo_pago', 'numero_operacion', 'observaciones', 'registrado_por']
    ordering = ['-fecha_pago']


class EstadoContratoInline(admin.TabularInline):
    """Inline para historial de estados"""
    model = EstadoContrato
    extra = 0
    readonly_fields = ['estado_anterior', 'estado_nuevo', 'cambiado_por', 'fecha_cambio']
    fields = ['estado_anterior', 'estado_nuevo', 'motivo', 'cambiado_por', 'fecha_cambio']
    ordering = ['-fecha_cambio']


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    """Admin para gestión de contratos"""
    form = ContratoAdminForm
    list_display = [
        'numero_contrato_display', 'cliente_nombre', 'tipo_servicio_display',
        'estado_indicator', 'monto_total_display', 'adelanto_display',
        'fecha_rango', 'vencimiento_indicator', 'creado_en_formateado', 'tenant'
    ]
    list_filter = ['estado', 'tipo_servicio', 'fecha_inicio', 'creado_en', 'tenant']
    search_fields = [
        'numero_contrato', 'titulo', 'cliente__nombres', 'cliente__apellidos',
        'cliente__razon_social'
    ]
    ordering = ['-creado_en']
    inlines = [ClausulaContratoInline, PagoContratoInline, EstadoContratoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tenant', 'numero_contrato', 'cliente', 'titulo', 'descripcion', 'tipo_servicio')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Información Financiera', {
            'fields': ('monto_total', 'adelanto', 'saldo_pendiente')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Documentos', {
            'fields': ('documento_contrato',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['saldo_pendiente', 'creado_en', 'actualizado_en']
    
    def get_fields(self, request, obj=None):
        """Mostrar tenant para todos los usuarios, pero controlar su edición"""
        fields = list(super().get_fields(request, obj))
        
        # Siempre mostrar tenant, pero será readonly para no superusuarios
        # Esto permite que se muestre el valor pero no se pueda editar
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer readonly algunos campos según el usuario"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # Para no superusuarios, tenant siempre debe ser readonly
        if not request.user.is_superuser:
            if 'tenant' not in readonly_fields:
                readonly_fields.append('tenant')
        # Para superusuarios, tenant es readonly solo al editar objeto existente
        elif request.user.is_superuser and obj:
            if 'tenant' not in readonly_fields:
                readonly_fields.append('tenant')
        
        return readonly_fields
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar el formulario para establecer valores por defecto"""
        form_class = super().get_form(request, obj, **kwargs)
        
        # Personalizar el formulario para mapear errores y fijar tenant
        class CustomForm(form_class):
            def __init__(self, *args, **kwargs):
                self.request = request
                super().__init__(*args, **kwargs)
                # Configurar el campo tenant según el usuario
                if 'tenant' in self.fields:
                    if not self.request.user.is_superuser:
                        user_tenant = getattr(self.request.user, 'tenant', None)
                        self.fields['tenant'].queryset = (
                            Tenant.objects.filter(id=user_tenant.id) if user_tenant else Tenant.objects.none()
                        )
                        self.fields['tenant'].initial = user_tenant
                        self.fields['tenant'].empty_label = None
                        # Deshabilitar edición en el formulario para no superusuarios
                        self.fields['tenant'].disabled = True

            def clean(self):
                cleaned_data = super().clean()
                # Validar y fijar tenant en el propio formulario
                if not self.request.user.is_superuser:
                    user_tenant = getattr(self.request.user, 'tenant', None)
                    if not user_tenant:
                        self.add_error('tenant', 'El usuario no tiene un tenant asignado')
                    else:
                        cleaned_data['tenant'] = user_tenant
                return cleaned_data

        return CustomForm
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar campos relacionados según el tenant del usuario"""
        from apps.crm.clientes.models import Cliente
        
        # Obtener el queryset base del campo
        if 'queryset' not in kwargs:
            kwargs['queryset'] = db_field.remote_field.model.objects.all()
        
        # Filtrar clientes por tenant
        if db_field.name == "cliente":
            if request.user.is_superuser:
                kwargs["queryset"] = Cliente.objects.all()
            elif hasattr(request.user, 'tenant') and request.user.tenant:
                kwargs["queryset"] = Cliente.objects.filter(tenant=request.user.tenant)
            else:
                kwargs["queryset"] = Cliente.objects.none()
        
        # Filtrar tenants
        elif db_field.name == "tenant":
            if request.user.is_superuser:
                kwargs["queryset"] = Tenant.objects.all()
            elif hasattr(request.user, 'tenant') and request.user.tenant:
                kwargs["queryset"] = Tenant.objects.filter(id=request.user.tenant.id)
            else:
                kwargs["queryset"] = Tenant.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def numero_contrato_display(self, obj):
        """Mostrar número de contrato con icono"""
        return f"📄 {obj.numero_contrato}"
    numero_contrato_display.short_description = 'N° Contrato'
    numero_contrato_display.admin_order_field = 'numero_contrato'
    
    def cliente_nombre(self, obj):
        """Nombre del cliente"""
        return obj.cliente.obtener_nombre_completo()
    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'cliente__nombres'
    
    def tipo_servicio_display(self, obj):
        """Tipo de servicio con color"""
        colors = {
            'fotografia': 'blue',
            'enmarcado': 'green',
            'graduaciones': 'purple',
            'laser': 'orange',
            'evento': 'red',
            'personalizado': 'brown'
        }
        color = colors.get(obj.tipo_servicio, 'gray')
        return mark_safe(f'<span style="color: {color};">● {obj.get_tipo_servicio_display()}</span>')
    tipo_servicio_display.short_description = 'Servicio'
    
    def estado_indicator(self, obj):
        """Indicador de estado con color"""
        colors = {
            'borrador': 'gray',
            'activo': 'green',
            'completado': 'blue',
            'cancelado': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">● {obj.get_estado_display()}</span>')
    estado_indicator.short_description = 'Estado'
    
    def monto_total_display(self, obj):
        """Monto total formateado"""
        return f"S/ {obj.monto_total:,.2f}"
    monto_total_display.short_description = 'Monto Total'
    monto_total_display.admin_order_field = 'monto_total'
    
    def adelanto_display(self, obj):
        """Adelanto con porcentaje"""
        porcentaje = obj.porcentaje_adelanto
        color = 'green' if porcentaje >= 50 else 'orange' if porcentaje > 0 else 'red'
        return mark_safe(f'<span style="color: {color};">S/ {obj.adelanto:,.2f} ({porcentaje:.1f}%)</span>')
    adelanto_display.short_description = 'Adelanto'
    
    def fecha_rango(self, obj):
        """Rango de fechas del contrato"""
        return f"{obj.fecha_inicio.strftime('%d/%m/%Y')} - {obj.fecha_fin.strftime('%d/%m/%Y')}"
    fecha_rango.short_description = 'Período'
    
    def vencimiento_indicator(self, obj):
        """Indicador de vencimiento"""
        if obj.estado != 'activo':
            return '-'
        
        hoy = timezone.now().date()
        dias_restantes = (obj.fecha_fin - hoy).days
        
        if dias_restantes < 0:
            return mark_safe('<span style="color: red; font-weight: bold;">⚠️ VENCIDO</span>')
        elif dias_restantes <= 7:
            return mark_safe(f'<span style="color: orange; font-weight: bold;">⚡ {dias_restantes} días</span>')
        elif dias_restantes <= 30:
            return mark_safe(f'<span style="color: blue;">📅 {dias_restantes} días</span>')
        else:
            return mark_safe(f'<span style="color: green;">✅ {dias_restantes} días</span>')
    vencimiento_indicator.short_description = 'Vencimiento'
    
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
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el tenant del usuario"""
        # Si no es superusuario, asignar automáticamente su tenant
        if not request.user.is_superuser:
            if hasattr(request.user, 'tenant') and request.user.tenant:
                obj.tenant = request.user.tenant
            else:
                # Si no hay tenant, devolver un error asociado al campo tenant
                from django.core.exceptions import ValidationError
                raise ValidationError({'tenant': 'El usuario no tiene un tenant asignado'})
        
        # Guardar y capturar errores de integridad para mostrar mensajes claros
        from django.db import IntegrityError
        try:
            super().save_model(request, obj, form, change)
        except IntegrityError:
            # Probable violación de unique_together (tenant, numero_contrato)
            from django.core.exceptions import ValidationError
            raise ValidationError({'numero_contrato': 'Este número de contrato ya existe en su estudio.'})
    
    def has_add_permission(self, request):
        """Verificar permisos para agregar contratos"""
        # Usuarios sin tenant no pueden crear contratos
        if not request.user.is_superuser:
            if not (hasattr(request.user, 'tenant') and request.user.tenant):
                return False
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """Verificar permisos para modificar contratos"""
        if not request.user.is_superuser and obj:
            # Solo puede modificar contratos de su tenant
            if hasattr(request.user, 'tenant') and request.user.tenant:
                return obj.tenant == request.user.tenant
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Verificar permisos para eliminar contratos"""
        if not request.user.is_superuser and obj:
            # Solo puede eliminar contratos de su tenant
            if hasattr(request.user, 'tenant') and request.user.tenant:
                return obj.tenant == request.user.tenant
            return False
        return super().has_delete_permission(request, obj)
    
    actions = [
        'activar_contratos', 'completar_contratos', 'cancelar_contratos',
        'verificar_vencimientos', 'exportar_contratos', 'generar_pdfs_contratos'
    ]
    
    def activar_contratos(self, request, queryset):
        """Activar contratos seleccionados"""
        updated = queryset.update(estado='activo')
        self.message_user(request, f'{updated} contrato(s) activado(s).', messages.SUCCESS)
    activar_contratos.short_description = "Activar contratos seleccionados"
    
    def completar_contratos(self, request, queryset):
        """Completar contratos seleccionados"""
        updated = queryset.update(estado='completado')
        self.message_user(request, f'{updated} contrato(s) completado(s).', messages.SUCCESS)
    completar_contratos.short_description = "Completar contratos seleccionados"
    
    def cancelar_contratos(self, request, queryset):
        """Cancelar contratos seleccionados"""
        updated = queryset.update(estado='cancelado')
        self.message_user(request, f'{updated} contrato(s) cancelado(s).', messages.WARNING)
    cancelar_contratos.short_description = "Cancelar contratos seleccionados"
    
    def verificar_vencimientos(self, request, queryset):
        """Verificar contratos próximos a vencer"""
        from datetime import timedelta
        hoy = timezone.now().date()
        proximos_30_dias = hoy + timedelta(days=30)
        
        proximos_vencer = queryset.filter(
            fecha_fin__gte=hoy,
            fecha_fin__lte=proximos_30_dias,
            estado='activo'
        ).count()
        
        vencidos = queryset.filter(
            fecha_fin__lt=hoy,
            estado='activo'
        ).count()
        
        if vencidos > 0:
            self.message_user(
                request,
                f'⚠️ {vencidos} contrato(s) vencido(s) y {proximos_vencer} próximo(s) a vencer.',
                messages.WARNING
            )
        elif proximos_vencer > 0:
            self.message_user(
                request,
                f'📅 {proximos_vencer} contrato(s) próximo(s) a vencer en 30 días.',
                messages.INFO
            )
        else:
            self.message_user(
                request,
                '✅ No hay contratos vencidos o próximos a vencer.',
                messages.SUCCESS
            )
    verificar_vencimientos.short_description = "Verificar vencimientos"
    
    def exportar_contratos(self, request, queryset):
        """Exportar contratos seleccionados a Excel"""
        try:
            from .services import ContractExcelService
            
            excel_file = ContractExcelService.generate_contracts_report(
                queryset, request.user.tenant
            )
            
            filename = f"contratos_admin_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            response = HttpResponse(
                excel_file.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            self.message_user(
                request,
                f'Exportando {queryset.count()} contrato(s) a Excel.',
                messages.SUCCESS
            )
            
            return response
            
        except ImportError:
            self.message_user(
                request,
                'Servicio de Excel no disponible. Contacte al administrador.',
                messages.ERROR
            )
        except Exception as e:
            self.message_user(
                request,
                f'Error exportando contratos: {str(e)}',
                messages.ERROR
            )
    exportar_contratos.short_description = "Exportar contratos a Excel"
    
    def generar_pdfs_contratos(self, request, queryset):
        """Generar PDFs de contratos seleccionados"""
        try:
            from .services import ContractPDFService, PDFNotImplemented
            
            count = 0
            for contrato in queryset:
                try:
                    ContractPDFService.generate(contrato)
                    count += 1
                except Exception:
                    continue
            
            self.message_user(
                request,
                f'Se generaron {count} PDF(s) de {queryset.count()} contrato(s).',
                messages.SUCCESS if count > 0 else messages.WARNING
            )
            
        except PDFNotImplemented:
            self.message_user(
                request,
                'Servicio de PDF no disponible. Contacte al administrador.',
                messages.ERROR
            )
    generar_pdfs_contratos.short_description = "Generar PDFs de contratos"


@admin.register(PagoContrato)
class PagoContratoAdmin(admin.ModelAdmin):
    """Admin para pagos de contratos"""
    list_display = [
        'contrato_numero', 'fecha_pago', 'monto_display', 'metodo_pago_display',
        'numero_operacion', 'registrado_por'
    ]
    list_filter = ['metodo_pago', 'fecha_pago', 'registrado_por']
    search_fields = [
        'contrato__numero_contrato', 'numero_operacion', 'observaciones'
    ]
    ordering = ['-fecha_pago']
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('contrato', 'fecha_pago', 'monto', 'metodo_pago')
        }),
        ('Detalles', {
            'fields': ('numero_operacion', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('registrado_por', 'creado_en'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['registrado_por', 'creado_en']
    
    def contrato_numero(self, obj):
        """Número del contrato"""
        return obj.contrato.numero_contrato
    contrato_numero.short_description = 'N° Contrato'
    contrato_numero.admin_order_field = 'contrato__numero_contrato'
    
    def monto_display(self, obj):
        """Monto formateado"""
        return f"S/ {obj.monto:,.2f}"
    monto_display.short_description = 'Monto'
    monto_display.admin_order_field = 'monto'
    
    def metodo_pago_display(self, obj):
        """Método de pago con icono"""
        icons = {
            'efectivo': '💵',
            'transferencia': '🏦',
            'tarjeta': '💳',
            'yape': '📱',
            'plin': '📲',
            'otro': '💰'
        }
        icon = icons.get(obj.metodo_pago, '💰')
        return f"{icon} {obj.get_metodo_pago_display()}"
    metodo_pago_display.short_description = 'Método'
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(contrato__tenant=request.user.tenant)
        return qs.none()