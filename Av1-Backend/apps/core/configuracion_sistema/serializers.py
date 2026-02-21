"""
Serializers del Módulo de Configuración del Sistema - Arte Ideas
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.multitenancy.models import Tenant
from apps.core.autenticacion.models import RolePermission

User = get_user_model()


class TenantSerializer(serializers.ModelSerializer):
    """Serializer para configuración del tenant/negocio"""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'description', 'is_active',
            'business_name', 'business_address', 'business_phone',
            'business_email', 'business_ruc', 'currency', 'location_type',
            'max_users', 'max_storage_mb', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class SuperAdminTenantSerializer(serializers.ModelSerializer):
    """Serializer para vista de super admin de tenants"""
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'description', 'is_active',
            'business_name', 'location_type', 'max_users', 'max_storage_mb',
            'users_count', 'created_at', 'updated_at'
        ]
    
    def get_users_count(self, obj):
        return obj.user_set.count()


class UserManagementSerializer(serializers.ModelSerializer):
    """Serializer para gestión de usuarios"""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'is_new_user', 'email_verified',
            'phone', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'created_at', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_role_display(self, obj):
        return obj.get_role_display()


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos usuarios"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'password', 'confirm_password'
        ]
    
    def validate(self, attrs):
        """Validar datos del usuario"""
        # Verificar que las contraseñas coincidan
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden'
            })
        
        # Verificar que el username no exista
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({
                'username': 'Este nombre de usuario ya existe'
            })
        
        # Verificar que el email no exista
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'Este email ya está en uso'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Crear nuevo usuario"""
        # Remover confirm_password
        validated_data.pop('confirm_password')
        
        # Obtener tenant del usuario que crea
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant
        
        # Crear usuario
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer para permisos de roles"""
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'role_display',
            # Módulos
            'access_dashboard', 'access_agenda', 'access_pedidos', 'access_clientes',
            'access_inventario', 'access_activos', 'access_gastos', 'access_produccion',
            'access_contratos', 'access_reportes',
            # Acciones sensibles
            'view_costos', 'view_precios', 'view_margenes', 'view_datos_clientes',
            'view_datos_financieros', 'edit_precios', 'delete_registros',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'role', 'created_at', 'updated_at']
    
    def get_role_display(self, obj):
        return obj.get_role_display()