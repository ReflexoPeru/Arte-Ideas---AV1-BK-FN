from django import forms
from .models import Activo, Financiamiento, Mantenimiento, Repuesto

class ActivoForm(forms.ModelForm):
    fecha_compra = forms.DateField(
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Activo
        fields = [
            'nombre', 'categoria', 'proveedor', 'fecha_compra', 'costo_total',
            'tipo_pago', 'vida_util', 'depreciacion_mensual', 'estado'
        ]


class ActivoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Mostrar nombre del activo y su costo total en la opción
        return f"{obj.nombre} - {obj.costo_total}"


class FinanciamientoForm(forms.ModelForm):
    fecha_inicio = forms.DateField(
        input_formats=['%Y-%m-%d']
    )
    fecha_fin = forms.DateField(
        input_formats=['%Y-%m-%d']
    )

    # Sobrescribir el campo para mostrar nombre + costo
    activo = ActivoChoiceField(queryset=Activo.objects.all())

    class Meta:
        model = Financiamiento
        fields = [
            'activo', 'tipo_pago', 'entidad_financiera', 'monto_financiado',
            'cuotas_totales', 'cuota_mensual', 'fecha_inicio', 'fecha_fin', 'estado'
        ]
        widgets = {}


class MantenimientoForm(forms.ModelForm):
    fecha_mantenimiento = forms.DateField(
        input_formats=['%Y-%m-%d']
    )
    proxima_fecha_mantenimiento = forms.DateField(
        input_formats=['%Y-%m-%d']
    ) 

    class Meta:
        model = Mantenimiento
        fields = [
            'activo', 'tipo_mantenimiento', 'fecha_mantenimiento', 'proveedor', 'estado_del_mantenimiento', 'costo', 'estado_del_activo', "proxima_fecha_mantenimiento", "descripcion"
        ]
        widgets = {}


class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = [
            'nombre', 'categoria', 'ubicacion', 'proveedor', 'codigo',
            'stock_actual', 'stock_minimo', 'costo_unitario', 'descripcion'
        ]
        widgets = {}
