"""
Serializers del Módulo de Usuarios - Arte Ideas
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para datos del usuario"""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'role', 'role_display', 'address', 'bio',
            'is_new_user', 'email_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'created_at', 'updated_at', 'is_new_user']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_role_display(self, obj):
        return obj.get_role_display()


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas del usuario"""
    orders_processed = serializers.IntegerField()
    clients_attended = serializers.IntegerField()
    sessions_completed = serializers.IntegerField()
    hours_worked = serializers.IntegerField()


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer para actividad del usuario"""
    action_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'action', 'action_display', 'description', 'module',
            'created_at'
        ]
    
    def get_action_display(self, obj):
        return obj.get_action_display()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validar contraseñas"""
        user = self.context['request'].user
        
        # Verificar contraseña actual
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError({
                'current_password': 'La contraseña actual es incorrecta'
            })
        
        # Verificar que las nuevas contraseñas coincidan
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden'
            })
        
        return attrs


class ChangeEmailSerializer(serializers.Serializer):
    """Serializer para cambio de email"""
    new_email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validar cambio de email"""
        user = self.context['request'].user
        
        # Verificar contraseña
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError({
                'password': 'La contraseña es incorrecta'
            })
        
        # Verificar que el email no esté en uso
        if User.objects.filter(email=attrs['new_email']).exclude(id=user.id).exists():
            raise serializers.ValidationError({
                'new_email': 'Este email ya está en uso'
            })
        
        return attrs