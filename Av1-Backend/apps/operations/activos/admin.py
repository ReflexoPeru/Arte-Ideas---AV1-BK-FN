from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal
from .models import Activo, Financiamiento, Mantenimiento, Repuesto

# Register your models here.

@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo_total', 'categoria', 'proveedor', 'fecha_compra', 'tipo_pago', 'vida_util', 'depreciacion_mensual', 'estado')
    list_filter = ('categoria', 'tipo_pago', 'estado', 'proveedor')
    search_fields = ('nombre', 'proveedor')
    
    def save_model(self, request, obj, form, change):
        """Sobrescribir save_model para manejar financiamientos automáticamente"""
        super().save_model(request, obj, form, change)
        
        # Si el activo es financiado o leasing, crear/actualizar financiamiento
        if obj.tipo_pago in ['financiado', 'leasing']:
            financiamiento, created = Financiamiento.objects.get_or_create(
                activo=obj,
                defaults={
                    'tipo_pago': obj.tipo_pago,
                    'entidad_financiera': 'Por definir',
                    'monto_financiado': obj.costo_total * Decimal('0.8') if obj.tipo_pago == 'financiado' else obj.costo_total,
                    'cuotas_totales': 24 if obj.tipo_pago == 'financiado' else 60,
                    'cuota_mensual': (obj.costo_total * Decimal('0.8')) / 24 if obj.tipo_pago == 'financiado' else obj.costo_total / 60,
                    'fecha_inicio': date.today(),
                    'fecha_fin': date.today() + timedelta(days=730) if obj.tipo_pago == 'financiado' else date.today() + timedelta(days=1825),
                    'estado': 'activo'
                }
            )
            
            if created:
                messages.success(request, f'✅ Registro de financiamiento creado automáticamente para {obj.nombre}')
            else:
                # Actualizar tipo de pago si cambió
                financiamiento.tipo_pago = obj.tipo_pago
                financiamiento.save()
                messages.info(request, f'ℹ️ Registro de financiamiento actualizado para {obj.nombre}')
        else:
            # Si ya no es financiado, eliminar financiamiento existente
            deleted_count = Financiamiento.objects.filter(activo=obj).delete()[0]
            if deleted_count > 0:
                messages.warning(request, f'⚠️ Registro de financiamiento eliminado para {obj.nombre} (ya no es financiado)')

@admin.register(Financiamiento)
class FinanciamientoAdmin(admin.ModelAdmin):
    list_display = ('activo', 'tipo_pago', 'entidad_financiera', 'monto_financiado', 'cuota_mensual', 'cuotas_totales', 'estado')
    list_filter = ('tipo_pago', 'estado', 'entidad_financiera')
    search_fields = ('activo__nombre', 'entidad_financiera')
    
    fieldsets = (
        ('Información del Activo', {
            'fields': ('activo', 'tipo_pago')
        }),
        ('Información del Financiamiento', {
            'fields': ('entidad_financiera', 'monto_financiado', 'cuotas_totales', 'cuota_mensual')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer activo readonly solo cuando se edita, no cuando se crea"""
        if obj:  # Si se está editando un objeto existente
            return ('activo',)
        return ()  # Si se está creando, permitir seleccionar el activo
    
    def get_queryset(self, request):
        """Solo mostrar financiamientos de activos que realmente son financiados/leasing"""
        return super().get_queryset(request).filter(activo__tipo_pago__in=['financiado', 'leasing'])
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar activos para mostrar solo los que son financiados/leasing"""
        if db_field.name == "activo":
            # Obtener todos los activos financiados/leasing sin ningún filtro adicional
            # Usar select_related si hay relaciones para optimizar
            queryset = Activo.objects.filter(
                tipo_pago__in=['financiado', 'leasing']
            ).order_by('nombre')
            
            # Debug: Verificar cuántos activos hay disponibles
            count = queryset.count()
            if count == 0:
                # Si no hay activos, verificar si hay activos en total
                total_activos = Activo.objects.count()
                if total_activos > 0:
                    # Hay activos pero ninguno es financiado/leasing
                    tipos_pago = Activo.objects.values_list('tipo_pago', flat=True).distinct()
                    messages.warning(
                        request,
                        f'⚠️ No hay activos con tipo de pago "Financiado" o "Leasing". '
                        f'Activos encontrados: {total_activos}. '
                        f'Tipos de pago disponibles: {", ".join(tipos_pago)}. '
                        f'Por favor, crea un activo con tipo de pago "Financiado" o "Leasing".'
                    )
                else:
                    messages.info(
                        request,
                        'ℹ️ No hay activos registrados. Crea primero un activo con tipo de pago "Financiado" o "Leasing".'
                    )
            
            kwargs["queryset"] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def add_view(self, request, form_url='', extra_context=None):
        """Vista personalizada para agregar financiamiento"""
        # Verificar activos disponibles antes de mostrar el formulario
        activos_disponibles = Activo.objects.filter(
            tipo_pago__in=['financiado', 'leasing']
        ).count()
        
        if activos_disponibles == 0:
            messages.warning(
                request,
                '⚠️ No hay activos disponibles para financiamiento. '
                'Asegúrate de crear activos con tipo de pago "Financiado" o "Leasing" primero.'
            )
        
        return super().add_view(request, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """Validar y sincronizar el tipo_pago con el activo seleccionado"""
        # Validar que se haya seleccionado un activo
        if not obj.activo:
            raise ValidationError('Debe seleccionar un activo para el financiamiento.')
        
        # Si se está creando un nuevo financiamiento, validar que el activo sea financiado/leasing
        if not change:
            if obj.activo.tipo_pago not in ['financiado', 'leasing']:
                raise ValidationError(
                    f'El activo "{obj.activo.nombre}" no es de tipo financiado o leasing. '
                    f'Tipo actual: {obj.activo.get_tipo_pago_display()}. '
                    f'Por favor, seleccione un activo que sea financiado o leasing.'
                )
            # Sincronizar el tipo_pago del financiamiento con el del activo si no se ha especificado
            if not obj.tipo_pago:
                obj.tipo_pago = obj.activo.tipo_pago
        
        super().save_model(request, obj, form, change)

@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ('activo', 'proxima_fecha_mantenimiento', 'tipo_mantenimiento', 'fecha_mantenimiento', 'proveedor', 'costo', 'descripcion', 'estado_del_mantenimiento','estado_del_activo')

@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'ubicacion', 'proveedor', 'stock_actual', 'stock_minimo', 'costo_unitario')
    list_filter = ('categoria', 'ubicacion', 'proveedor')
    search_fields = ('nombre', 'codigo', 'proveedor', 'descripcion')
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'categoria', 'proveedor')
        }),
        ('Inventario', {
            'fields': ('ubicacion', 'stock_actual', 'stock_minimo', 'costo_unitario')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
    )
