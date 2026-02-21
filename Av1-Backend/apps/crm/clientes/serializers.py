"""
Serializers del Módulo de Clientes - Arte Ideas CRM
"""
from rest_framework import serializers
from .models import Cliente, HistorialCliente, ContactoCliente


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer completo para clientes"""
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    nombre_completo = serializers.ReadOnlyField(source='obtener_nombre_completo')
    
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate(self, attrs):
        """Validaciones personalizadas"""
        tipo_cliente = attrs.get('tipo_cliente')
        
        # Validar campos específicos según tipo de cliente
        if tipo_cliente == 'empresa':
            if not attrs.get('razon_social'):
                raise serializers.ValidationError({
                    'razon_social': 'La razón social es obligatoria para empresas'
                })
        
        elif tipo_cliente == 'colegio':
            if not attrs.get('nivel_educativo'):
                raise serializers.ValidationError({
                    'nivel_educativo': 'El nivel educativo es obligatorio para colegios'
                })
        
        return attrs


class ClienteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de clientes"""
    nombre_completo = serializers.ReadOnlyField(source='obtener_nombre_completo')
    tipo_cliente_display = serializers.ReadOnlyField(source='get_tipo_cliente_display')
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre_completo', 'tipo_cliente', 'tipo_cliente_display',
            'email', 'telefono', 'dni', 'razon_social', 'activo', 'creado_en'
        ]


class HistorialClienteSerializer(serializers.ModelSerializer):
    """Serializer para historial de clientes"""
    tipo_interaccion_display = serializers.ReadOnlyField(source='get_tipo_interaccion_display')
    registrado_por_nombre = serializers.ReadOnlyField(source='registrado_por.get_full_name')
    cliente_nombre = serializers.ReadOnlyField(source='cliente.obtener_nombre_completo')
    
    class Meta:
        model = HistorialCliente
        fields = '__all__'


class ContactoClienteSerializer(serializers.ModelSerializer):
    """Serializer para contactos de clientes"""
    cliente_nombre = serializers.ReadOnlyField(source='cliente.obtener_nombre_completo')
    
    class Meta:
        model = ContactoCliente
        fields = '__all__'


class ClienteEstadisticasSerializer(serializers.Serializer):
    """Serializer para estadísticas de clientes"""
    total_clientes = serializers.IntegerField()
    clientes_activos = serializers.IntegerField()
    clientes_inactivos = serializers.IntegerField()
    por_tipo = serializers.DictField()
    colegios_por_nivel = serializers.DictField()