"""
Modelos de Multi-tenancy - Arte Ideas
Modelos relacionados con tenants y configuraciones específicas
"""
from django.db import models


class Tenant(models.Model):
    """
    Modelo para estudios fotográficos (tenants)
    Cada tenant representa un estudio fotográfico independiente
    """
    # Usar AutoField simple para testing fácil
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Nombre del Estudio')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Identificador')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Configuración específica por tenant
    max_users = models.IntegerField(default=10, verbose_name='Máximo de Usuarios')
    max_storage_mb = models.IntegerField(default=1000, verbose_name='Almacenamiento Máximo (MB)')
    
    # Configuración del negocio (datos que se ven en la imagen)
    business_name = models.CharField(max_length=200, verbose_name='Nombre de la Empresa')
    business_address = models.TextField(verbose_name='Dirección')
    business_phone = models.CharField(max_length=15, verbose_name='Teléfono')
    business_email = models.EmailField(verbose_name='Email Corporativo')
    business_ruc = models.CharField(max_length=11, verbose_name='RUC')
    currency = models.CharField(
        max_length=10,
        choices=[
            ('PEN', 'Soles (S/)'),
            ('USD', 'Dólares ($)'),
            ('EUR', 'Euros (€)'),
        ],
        default='PEN',
        verbose_name='Moneda'
    )
    
    # Configuraciones de acceso (restricciones por ubicación)
    location_type = models.CharField(
        max_length=20,
        choices=[
            ('lima', 'Lima - Acceso Completo'),
            ('provincia', 'Provincia - Acceso Limitado'),
        ],
        default='lima',
        verbose_name='Tipo de Ubicación'
    )
    
    class Meta:
        verbose_name = 'Estudio Fotográfico'
        verbose_name_plural = 'Estudios Fotográficos'
        
    def __str__(self):
        return f"{self.name}"
        
    def save(self, *args, **kwargs):
        # Generar slug automáticamente si no existe
        if not self.slug:
            import re
            self.slug = re.sub(r'[^a-zA-Z0-9]', '', self.name.lower())[:50]
        super().save(*args, **kwargs)
        
    def has_global_data_access(self):
        """Verificar si el tenant tiene acceso a datos globales"""
        return self.location_type == 'lima'
        
    def has_financial_modules(self):
        """Verificar si el tenant tiene acceso a módulos financieros"""
        return self.location_type == 'lima'


class TenantConfiguration(models.Model):
    """
    Configuraciones específicas por tenant
    """
    MODULE_CHOICES = [
        ('general', 'General'),
        ('crm', 'CRM'),
        ('commerce', 'Commerce'),
        ('operations', 'Operations'),
        ('finance', 'Finance'),
        ('analytics', 'Analytics'),
    ]
    
    DATA_TYPE_CHOICES = [
        ('string', 'Texto'),
        ('integer', 'Número entero'),
        ('float', 'Número decimal'),
        ('boolean', 'Verdadero/Falso'),
        ('json', 'JSON'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Tenant')
    module = models.CharField(max_length=20, choices=MODULE_CHOICES, verbose_name='Módulo')
    key = models.CharField(max_length=100, verbose_name='Clave')
    value = models.TextField(verbose_name='Valor')
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default='string', verbose_name='Tipo de dato')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Metadatos
    is_editable = models.BooleanField(default=True, verbose_name='Editable')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Tenant'
        verbose_name_plural = 'Configuraciones del Tenant'
        unique_together = ['tenant', 'module', 'key']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.module}.{self.key}"
    
    def get_typed_value(self):
        """Obtener el valor con el tipo de dato correcto"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'float':
            return float(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.data_type == 'json':
            import json
            return json.loads(self.value)
        return self.value