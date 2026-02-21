"""
Signals del Módulo de Usuarios - Arte Ideas
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crear perfil de usuario automáticamente cuando se crea un usuario
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guardar perfil de usuario cuando se guarda el usuario
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Crear perfil si no existe
        UserProfile.objects.create(user=instance)