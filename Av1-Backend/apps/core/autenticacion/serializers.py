"""
Serializers del Módulo de Autenticación - Arte Ideas
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth.models import update_last_login

class LogoutSerializer(serializers.Serializer):
    """Serializer para logout"""
    refresh_token = serializers.CharField(required=True)
    
    def validate_refresh_token(self, value):
        """Validar que el refresh token no esté vacío"""
        if not value:
            raise serializers.ValidationError("El refresh token es requerido")
        return value


class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        User = get_user_model()
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'Email no encontrado'})
        
        if not user.is_active:
            raise serializers.ValidationError({'email': 'Cuenta inactiva'})
        
        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Contraseña incorrecta'})
        
        refresh = RefreshToken.for_user(user)
        
        if settings.SIMPLE_JWT.get('UPDATE_LAST_LOGIN', False):
            update_last_login(None, user)
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

