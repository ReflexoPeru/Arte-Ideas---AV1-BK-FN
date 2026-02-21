"""
Signals del Módulo de Autenticación - Arte Ideas
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import RolePermission

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_role_permissions(sender, instance, created, **kwargs):
    """
    Crear permisos por defecto para el rol del usuario si no existen
    """
    if created and instance.tenant and instance.role:
        # Verificar si ya existen permisos para este rol y tenant
        role_permission, created = RolePermission.objects.get_or_create(
            tenant=instance.tenant,
            role=instance.role,
            defaults=RolePermission.get_default_permissions(instance.role)
        )