"""
Serializers del Módulo de Activos - Arte Ideas Operations
"""
from rest_framework import serializers
from decimal import Decimal
from datetime import date, timedelta

from .models import Activo, Financiamiento, Mantenimiento, Repuesto


class ActivoSerializer(serializers.ModelSerializer):
    """Serializer para Activos"""
    valor_actual = serializers.SerializerMethodField()
    depreciacion_acumulada = serializers.SerializerMethodField()
    meses_transcurridos = serializers.SerializerMethodField()
    
    class Meta:
        model = Activo
        fields = [
            'id', 'nombre', 'categoria', 'proveedor', 'fecha_compra',
            'costo_total', 'tipo_pago', 'vida_util', 'depreciacion_mensual',
            'estado', 'valor_actual', 'depreciacion_acumulada', 'meses_transcurridos'
        ]
        read_only_fields = ['id', 'valor_actual', 'depreciacion_acumulada', 'meses_transcurridos']
    
    def get_meses_transcurridos(self, obj):
        """Calcular meses transcurridos desde la compra"""
        today = date.today()
        meses = (today.year - obj.fecha_compra.year) * 12 + (today.month - obj.fecha_compra.month)
        return max(0, meses)
    
    def get_depreciacion_acumulada(self, obj):
        """Calcular depreciación acumulada"""
        meses = self.get_meses_transcurridos(obj)
        return min(obj.depreciacion_mensual * meses, obj.costo_total)
    
    def get_valor_actual(self, obj):
        """Calcular valor actual del activo"""
        depreciacion = self.get_depreciacion_acumulada(obj)
        return obj.costo_total - depreciacion
    
    def validate_depreciacion_mensual(self, value):
        """Validar que la depreciación mensual sea coherente"""
        if value < 0:
            raise serializers.ValidationError("La depreciación mensual no puede ser negativa")
        return value
    
    def validate_vida_util(self, value):
        """Validar vida útil"""
        if value <= 0:
            raise serializers.ValidationError("La vida útil debe ser mayor a 0 meses")
        return value
    
    def validate_costo_total(self, value):
        """Validar costo total"""
        if value <= 0:
            raise serializers.ValidationError("El costo total debe ser mayor a 0")
        return value
    
    def validate(self, data):
        """Validaciones cruzadas"""
        if 'vida_util' in data and 'depreciacion_mensual' in data and 'costo_total' in data:
            vida_util = data['vida_util']
            depreciacion_mensual = data['depreciacion_mensual']
            costo_total = data['costo_total']
            
            # Verificar que la depreciación total no exceda el costo
            depreciacion_total = depreciacion_mensual * vida_util
            if depreciacion_total > costo_total:
                raise serializers.ValidationError({
                    'depreciacion_mensual': f'La depreciación total ({depreciacion_total}) no puede exceder el costo total ({costo_total})'
                })
        
        return data


class FinanciamientoSerializer(serializers.ModelSerializer):
    """Serializer para Financiamientos"""
    activo_nombre = serializers.CharField(source='activo.nombre', read_only=True)
    cuotas_pagadas = serializers.SerializerMethodField()
    cuotas_pendientes = serializers.SerializerMethodField()
    saldo_pendiente = serializers.SerializerMethodField()
    
    class Meta:
        model = Financiamiento
        fields = [
            'id', 'activo', 'activo_nombre', 'tipo_pago', 'entidad_financiera',
            'monto_financiado', 'cuotas_totales', 'cuota_mensual',
            'fecha_inicio', 'fecha_fin', 'estado',
            'cuotas_pagadas', 'cuotas_pendientes', 'saldo_pendiente'
        ]
        read_only_fields = ['id', 'cuotas_pagadas', 'cuotas_pendientes', 'saldo_pendiente']
    
    def get_cuotas_pagadas(self, obj):
        """Calcular cuotas pagadas basado en la fecha actual"""
        today = date.today()
        if today < obj.fecha_inicio:
            return 0
        
        meses_transcurridos = (today.year - obj.fecha_inicio.year) * 12 + (today.month - obj.fecha_inicio.month)
        return min(meses_transcurridos, obj.cuotas_totales)
    
    def get_cuotas_pendientes(self, obj):
        """Calcular cuotas pendientes"""
        return obj.cuotas_totales - self.get_cuotas_pagadas(obj)
    
    def get_saldo_pendiente(self, obj):
        """Calcular saldo pendiente"""
        cuotas_pendientes = self.get_cuotas_pendientes(obj)
        return cuotas_pendientes * obj.cuota_mensual
    
    def validate(self, data):
        """Validaciones cruzadas"""
        if 'monto_financiado' in data and 'cuotas_totales' in data and 'cuota_mensual' in data:
            monto = data['monto_financiado']
            cuotas = data['cuotas_totales']
            cuota_mensual = data['cuota_mensual']
            
            # Verificar coherencia entre monto, cuotas y cuota mensual
            total_cuotas = cuota_mensual * cuotas
            diferencia = abs(total_cuotas - monto)
            
            # Permitir una diferencia pequeña por intereses
            if diferencia > monto * Decimal('0.5'):  # 50% de diferencia máxima
                raise serializers.ValidationError({
                    'cuota_mensual': f'Las cuotas totales ({total_cuotas}) difieren significativamente del monto financiado ({monto})'
                })
        
        if 'fecha_inicio' in data and 'fecha_fin' in data:
            if data['fecha_inicio'] >= data['fecha_fin']:
                raise serializers.ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
                })
        
        return data


class MantenimientoSerializer(serializers.ModelSerializer):
    """Serializer para Mantenimientos"""
    activo_nombre = serializers.CharField(source='activo.nombre', read_only=True)
    dias_hasta_proximo = serializers.SerializerMethodField()
    
    class Meta:
        model = Mantenimiento
        fields = [
            'id', 'activo', 'activo_nombre', 'tipo_mantenimiento',
            'fecha_mantenimiento', 'proveedor', 'costo',
            'estado_del_mantenimiento', 'estado_del_activo',
            'proxima_fecha_mantenimiento', 'descripcion', 'dias_hasta_proximo'
        ]
        read_only_fields = ['id', 'dias_hasta_proximo']
    
    def get_dias_hasta_proximo(self, obj):
        """Calcular días hasta el próximo mantenimiento"""
        if obj.proxima_fecha_mantenimiento:
            today = date.today()
            delta = obj.proxima_fecha_mantenimiento - today
            return delta.days
        return None
    
    def validate_fecha_mantenimiento(self, value):
        """Validar fecha de mantenimiento"""
        if value > date.today():
            # Permitir fechas futuras solo para mantenimientos programados
            return value
        return value
    
    def validate_costo(self, value):
        """Validar costo del mantenimiento"""
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo")
        return value


class RepuestoSerializer(serializers.ModelSerializer):
    """Serializer para Repuestos"""
    alerta_stock = serializers.SerializerMethodField()
    valor_total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Repuesto
        fields = [
            'id', 'nombre', 'categoria', 'ubicacion', 'proveedor',
            'codigo', 'stock_actual', 'stock_minimo', 'costo_unitario',
            'descripcion', 'alerta_stock', 'valor_total_stock'
        ]
        read_only_fields = ['id', 'alerta_stock', 'valor_total_stock']
    
    def get_alerta_stock(self, obj):
        """Verificar si el repuesto necesita reabastecimiento"""
        return obj.stock_actual <= obj.stock_minimo
    
    def get_valor_total_stock(self, obj):
        """Calcular valor total del stock"""
        return obj.stock_actual * obj.costo_unitario
    
    def validate_stock_actual(self, value):
        """Validar stock actual"""
        if value < 0:
            raise serializers.ValidationError("El stock actual no puede ser negativo")
        return value
    
    def validate_stock_minimo(self, value):
        """Validar stock mínimo"""
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo")
        return value
    
    def validate_costo_unitario(self, value):
        """Validar costo unitario"""
        if value < 0:
            raise serializers.ValidationError("El costo unitario no puede ser negativo")
        return value