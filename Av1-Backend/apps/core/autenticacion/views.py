"""
Views del Módulo de Autenticación - Arte Ideas
Gestión de login, logout, registro y autenticación
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from apps.core.usuarios.models import UserActivity

from .serializers import LogoutSerializer, EmailTokenObtainPairSerializer

User = get_user_model()

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Vista para logout de usuarios"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Cerrar sesión del usuario"""
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Obtener el refresh token
                refresh_token = serializer.validated_data['refresh_token']
                token = RefreshToken(refresh_token)
                
                # Invalidar el token (blacklist)
                token.blacklist()
                
                # Registrar actividad de logout
                UserActivity.objects.create(
                    user=request.user,
                    tenant=request.user.tenant,
                    action='logout',
                    description='Cerró sesión en el sistema',
                    module='auth'
                )
                
                return Response({
                    'message': 'Sesión cerrada exitosamente'
                }, status=status.HTTP_200_OK)
                
            except TokenError as e:
                return Response({
                    'error': 'Token inválido o ya expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
