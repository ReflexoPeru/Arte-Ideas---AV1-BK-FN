"""
Serializers del Módulo de Contratos - Arte Ideas CRM
"""
from rest_framework import serializers
from django.db.models import Sum
from .models import Contrato, ClausulaContrato, PagoContrato, EstadoContrato


class ContratoSerializer(serializers.ModelSerializer):
    """Serializer completo para contratos"""
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    cliente_nombre = serializers.ReadOnlyField(source='cliente.obtener_nombre_completo')
    porcentaje_adelanto = serializers.ReadOnlyField()
    esta_vencido = serializers.ReadOnlyField()
    
    class Meta:
        model = Contrato
        fields = '__all__'

    def validate(self, attrs):
        """Validaciones personalizadas"""
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
            })
        
        adelanto = attrs.get('adelanto', 0)
        monto_total = attrs.get('monto_total')
        
        if adelanto and monto_total and adelanto > monto_total:
            raise serializers.ValidationError({
                'adelanto': 'El adelanto no puede ser mayor al monto total'
            })
        
        return attrs


class ContratoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de contratos"""
    cliente_nombre = serializers.ReadOnlyField(source='cliente.obtener_nombre_completo')
    tipo_servicio_display = serializers.ReadOnlyField(source='get_tipo_servicio_display')
    estado_display = serializers.ReadOnlyField(source='get_estado_display')
    porcentaje_adelanto = serializers.ReadOnlyField()
    esta_vencido = serializers.ReadOnlyField()
    
    class Meta:
        model = Contrato
        fields = [
            'id', 'numero_contrato', 'titulo', 'cliente_nombre', 'tipo_servicio',
            'tipo_servicio_display', 'estado', 'estado_display', 'fecha_inicio',
            'fecha_fin', 'monto_total', 'adelanto', 'saldo_pendiente',
            'porcentaje_adelanto', 'esta_vencido', 'creado_en'
        ]


class ClausulaContratoSerializer(serializers.ModelSerializer):
    """Serializer para cláusulas de contratos"""
    
    class Meta:
        model = ClausulaContrato
        fields = '__all__'

    def validate(self, attrs):
        """Validar que no exista otra cláusula con el mismo número"""
        contrato = attrs.get('contrato')
        numero_clausula = attrs.get('numero_clausula')
        
        if contrato and numero_clausula:
            # Si estamos editando, excluir el objeto actual
            queryset = ClausulaContrato.objects.filter(
                contrato=contrato, 
                numero_clausula=numero_clausula
            )
            
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'numero_clausula': f'Ya existe una cláusula con el número {numero_clausula} en este contrato'
                })
        
        return attrs


class PagoContratoSerializer(serializers.ModelSerializer):
    """Serializer para pagos de contratos"""
    registrado_por_nombre = serializers.ReadOnlyField(source='registrado_por.get_full_name')
    contrato_numero = serializers.ReadOnlyField(source='contrato.numero_contrato')
    metodo_pago_display = serializers.ReadOnlyField(source='get_metodo_pago_display')
    
    class Meta:
        model = PagoContrato
        fields = '__all__'

    def validate(self, attrs):
        """Validaciones para pagos"""
        monto = attrs.get('monto')
        contrato = attrs.get('contrato')
        
        if monto and monto <= 0:
            raise serializers.ValidationError({
                'monto': 'El monto debe ser mayor a 0'
            })
        
        if contrato and monto:
            # Verificar que el pago no exceda el saldo pendiente
            total_pagos_anteriores = PagoContrato.objects.filter(
                contrato=contrato
            ).aggregate(total=Sum('monto'))['total'] or 0
            
            if self.instance:
                # Si estamos editando, restar el monto anterior
                total_pagos_anteriores -= self.instance.monto
            
            nuevo_total_pagos = total_pagos_anteriores + monto
            
            if nuevo_total_pagos > contrato.monto_total:
                exceso = nuevo_total_pagos - contrato.monto_total
                raise serializers.ValidationError({
                    'monto': f'El pago excede el monto del contrato en S/ {exceso:.2f}'
                })
        
        return attrs


class EstadoContratoSerializer(serializers.ModelSerializer):
    """Serializer para historial de estados de contratos"""
    cambiado_por_nombre = serializers.ReadOnlyField(source='cambiado_por.get_full_name')
    contrato_numero = serializers.ReadOnlyField(source='contrato.numero_contrato')
    estado_anterior_display = serializers.ReadOnlyField(source='get_estado_anterior_display')
    estado_nuevo_display = serializers.ReadOnlyField(source='get_estado_nuevo_display')
    
    class Meta:
        model = EstadoContrato
        fields = '__all__'


class ContratoEstadisticasSerializer(serializers.Serializer):
    """Serializer para estadísticas de contratos"""
    total_contratos = serializers.IntegerField()
    contratos_activos = serializers.IntegerField()
    contratos_completados = serializers.IntegerField()
    contratos_cancelados = serializers.IntegerField()
    contratos_vencidos = serializers.IntegerField()
    montos = serializers.DictField()
    por_tipo_servicio = serializers.DictField()