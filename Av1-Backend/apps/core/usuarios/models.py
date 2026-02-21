"""
Modelos de Usuarios - Arte Ideas
Modelos relacionados con perfiles de usuario y actividades
"""
from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """
    Perfil extendido del usuario (datos adicionales)
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    # Preferencias del usuario
    language = models.CharField(
        max_length=10,
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
        ],
        default='es',
        verbose_name='Idioma'
    )
    theme = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Claro'),
            ('dark', 'Oscuro'),
        ],
        default='light',
        verbose_name='Tema'
    )
    
    # Configuraciones de notificaciones
    email_notifications = models.BooleanField(default=True, verbose_name='Notificaciones Email')
    
    # Estadísticas (calculadas dinámicamente)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"


class UserActivity(models.Model):
    """
    Registro de actividad del usuario
    """
    ACTION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('create', 'Crear registro'),
        ('update', 'Actualizar registro'),
        ('delete', 'Eliminar registro'),
        ('export', 'Exportar datos'),
        ('config_change', 'Cambio de configuración'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    tenant = models.ForeignKey('multitenancy.Tenant', on_delete=models.CASCADE, verbose_name='Tenant')
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='Acción')
    description = models.TextField(verbose_name='Descripción')
    module = models.CharField(max_length=50, blank=True, verbose_name='Módulo')
    
    # Metadatos
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dirección IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Actividad de Usuario'
        verbose_name_plural = 'Actividades de Usuario'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"