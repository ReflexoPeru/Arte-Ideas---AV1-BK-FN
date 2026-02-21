from rest_framework import serializers
from .models import OrdenProduccion
from apps.core.models import User, Tenant
from apps.crm.models import Cliente
from apps.commerce.models import Order

class OrdenProduccionSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.ReadOnlyField(source='cliente.obtener_nombre_completo')
    operario_nombre = serializers.ReadOnlyField(source='operario.get_full_name')
    pedido_codigo = serializers.ReadOnlyField(source='pedido.order_number')
    
    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'numero_op', 'pedido', 'pedido_codigo', 'cliente', 'cliente_nombre', 
            'descripcion', 'tipo', 'estado', 'prioridad', 'operario', 
            'operario_nombre', 'fecha_estimada', 'tenant',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en', 'tenant', 'cliente']  # cliente se autocompleta
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user_tenant = self.context.get('user_tenant')
        
        # Filtrar campos relacionados por tenant
        if user_tenant:
            # Solo pedidos del mismo tenant
            self.fields['pedido'].queryset = Order.objects.filter(tenant=user_tenant)
            # Solo operarios del mismo tenant
            self.fields['operario'].queryset = User.objects.filter(
                role='operario',
                tenant=user_tenant
            )
        
        # Ocultar tenant para usuarios no superusuarios
        if request and hasattr(request, 'user'):
            if not request.user.is_superuser:
                # Remover tenant de los campos visibles
                if 'tenant' in self.fields:
                    del self.fields['tenant']
    

    
    def create(self, validated_data):
        """Asignar automáticamente cliente y tenant"""
        pedido = validated_data.get('pedido')
        request = self.context.get('request')
        
        # Autocompletar cliente según pedido
        if pedido:
            validated_data['cliente'] = pedido.cliente
        
        # Asignar automáticamente el tenant del usuario
        if request and hasattr(request.user, 'tenant') and request.user.tenant:
            validated_data['tenant'] = request.user.tenant
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Prevenir cambio de tenant en actualizaciones"""
        # Remover tenant de validated_data para prevenir cambios accidentales
        validated_data.pop('tenant', None)
        
        # Autocompletar cliente si se cambia el pedido
        pedido = validated_data.get('pedido')
        if pedido:
            validated_data['cliente'] = pedido.cliente
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """Personalizar la representación según el tipo de usuario"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Solo mostrar tenant a superusuarios
        if request and hasattr(request, 'user'):
            if not request.user.is_superuser and 'tenant' in data:
                del data['tenant']
        
        return data
    
    def validate_numero_op(self, value):
        # Verificar que el número de OP sea único
        if OrdenProduccion.objects.filter(numero_op=value).exists():
            if self.instance and self.instance.numero_op == value:
                return value
            raise serializers.ValidationError("Este número de orden ya existe.")
        return value
    
    def validate_operario(self, value):
        # Verificar que el operario tenga el rol correcto
        if value and value.role != 'operario':
            raise serializers.ValidationError("El usuario seleccionado no tiene el rol de Operario.")
        return value
    
    def validate(self, data):
        # Verificar que todos los campos requeridos estén presentes
        # Nota: tenant y cliente se asignan automáticamente, no son requeridos en la validación
        required_fields = ['numero_op', 'pedido', 'descripcion', 
                          'tipo', 'estado', 'prioridad', 'operario', 
                          'fecha_estimada']
        
        for field in required_fields:
            if field not in data and (not self.instance or not getattr(self.instance, field)):
                raise serializers.ValidationError({field: "Este campo es requerido."})
        
        return data