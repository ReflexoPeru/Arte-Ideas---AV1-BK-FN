"""
Views del Módulo de Usuarios - Arte Ideas
Gestión de perfiles de usuario y actividades
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import UserActivity
import random

from .serializers import (
    UserSerializer, UserStatisticsSerializer, UserActivitySerializer,
    ChangePasswordSerializer, ChangeEmailSerializer
)

User = get_user_model()


class ProfileView(APIView):
    """Vista para gestión del perfil personal"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener datos del perfil actual"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Actualizar perfil personal"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Registrar actividad
            UserActivity.objects.create(
                user=request.user,
                tenant=request.user.tenant,
                action='update',
                description='Actualizó su perfil personal',
                module='profile'
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileStatisticsView(APIView):
    """Vista para estadísticas del usuario"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener estadísticas mensuales del usuario"""
        # Datos simulados basados en las imágenes del frontend
        # En producción, estos se calcularían desde las otras apps
        user = request.user
        
        # Generar estadísticas simuladas pero consistentes por usuario
        random.seed(hash(str(user.id)))
        
        stats = {
            'orders_processed': random.randint(150, 300),
            'clients_attended': random.randint(50, 120),
            'sessions_completed': random.randint(30, 80),
            'hours_worked': random.randint(120, 200)
        }
        
        serializer = UserStatisticsSerializer(stats)
        return Response(serializer.data)


class ProfileCompletionView(APIView):
    """Vista para porcentaje de completitud del perfil"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener porcentaje de completitud del perfil"""
        user = request.user
        fields = [
            user.first_name, user.last_name, user.email,
            user.phone, user.address, user.bio
        ]
        completed = sum(1 for field in fields if field)
        percentage = int((completed / len(fields)) * 100)
        
        return Response({
            'completion_percentage': percentage,
            'completed_fields': completed,
            'total_fields': len(fields)
        })


class ProfileActivityView(APIView):
    """Vista para actividad reciente del usuario"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener actividad reciente del usuario"""
        activities = UserActivity.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """Vista para cambio de contraseña"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Cambiar contraseña del usuario"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Registrar actividad
            UserActivity.objects.create(
                user=user,
                tenant=user.tenant,
                action='update',
                description='Cambió su contraseña',
                module='security'
            )
            
            return Response({'message': 'Contraseña actualizada correctamente'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(APIView):
    """Vista para cambio de email"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Cambiar email del usuario"""
        serializer = ChangeEmailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            old_email = user.email
            user.email = serializer.validated_data['new_email']
            user.email_verified = False  # Requiere nueva verificación
            user.save()
            
            # Registrar actividad
            UserActivity.objects.create(
                user=user,
                tenant=user.tenant,
                action='update',
                description=f'Cambió su email de {old_email} a {user.email}',
                module='security'
            )
            
            return Response({'message': 'Email actualizado correctamente'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)