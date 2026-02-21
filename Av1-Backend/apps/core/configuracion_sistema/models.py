"""
Modelos de Configuración del Sistema - Arte Ideas
Configuraciones globales y específicas por tenant
"""
from django.db import models


class SystemConfiguration(models.Model):
    """
    Configuraciones globales del sistema (compartidas entre tenants)
    """
    key = models.CharField(max_length=100, unique=True, verbose_name='Clave')
    value = models.TextField(verbose_name='Valor')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
        
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"