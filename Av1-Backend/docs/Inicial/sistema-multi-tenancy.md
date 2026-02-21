# 🏢 Sistema Multi-Tenancy - Arte Ideas

## 🎯 Estrategia: Shared Database + Tenant Isolation

**Arte Ideas** implementa multi-tenancy usando una **base de datos única** con **aislamiento por `tenant_id`**, optimizando costos y mantenimiento mientras garantiza seguridad y escalabilidad.

## 🏗️ Arquitectura Multi-Tenant

### Modelo Base: Tenant
```python
# core/models.py
class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    settings = models.JSONField(default=dict)
    
    # Configuración específica por tenant
    max_users = models.IntegerField(default=10)
    max_storage_mb = models.IntegerField(default=1000)
    features_enabled = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} ({self.subdomain})"
```

### Patrón de Modelos Multi-Tenant
```python
# Ejemplo en cualquier app
class BaseModel(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        # Validar que el tenant esté activo
        if not self.tenant.is_active:
            raise ValidationError("Tenant is not active")
        super().save(*args, **kwargs)

# Implementación en cada modelo
class Client(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    # ... otros campos
    
    class Meta:
        unique_together = ['tenant', 'email']  # Email único por tenant
```

## 🔒 Middleware de Tenant

### TenantMiddleware
```python
# core/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from .models import Tenant

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Obtener tenant desde subdomain o header
        tenant = self.get_tenant(request)
        
        if not tenant:
            raise Http404("Tenant not found")
            
        if not tenant.is_active:
            raise Http404("Tenant is not active")
            
        # Agregar tenant al request
        request.tenant = tenant
        
        # Configurar contexto global para queries
        from .context import set_current_tenant
        set_current_tenant(tenant)
        
    def get_tenant(self, request):
        # Método 1: Por subdomain
        host = request.get_host()
        subdomain = host.split('.')[0]
        
        try:
            return Tenant.objects.get(subdomain=subdomain, is_active=True)
        except Tenant.DoesNotExist:
            pass
            
        # Método 2: Por header (para APIs)
        tenant_id = request.META.get('HTTP_X_TENANT_ID')
        if tenant_id:
            try:
                return Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                pass
                
        # Método 3: Por JWT token
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user.tenant
            
        return None
```

### Context Manager para Tenant
```python
# core/context.py
import threading

_thread_local = threading.local()

def set_current_tenant(tenant):
    _thread_local.tenant = tenant

def get_current_tenant():
    return getattr(_thread_local, 'tenant', None)

def clear_current_tenant():
    if hasattr(_thread_local, 'tenant'):
        delattr(_thread_local, 'tenant')
```

## 🔍 QuerySet Manager Multi-Tenant

### Manager Automático
```python
# core/managers.py
from django.db import models
from .context import get_current_tenant

class TenantManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return queryset.filter(tenant=tenant)
        return queryset.none()  # Sin tenant, sin datos
        
    def all_tenants(self):
        """Método para acceder a datos de todos los tenants (admin)"""
        return super().get_queryset()

# Aplicación en modelos
class Client(BaseModel):
    name = models.CharField(max_length=100)
    # ... otros campos
    
    objects = TenantManager()  # Manager por defecto con filtro
    all_objects = models.Manager()  # Manager sin filtro para admin
```

### ViewSet Base Multi-Tenant
```python
# core/viewsets.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import TenantPermission

class TenantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TenantPermission]
    
    def get_queryset(self):
        # El manager ya filtra por tenant automáticamente
        return self.queryset.all()
        
    def perform_create(self, serializer):
        # Asignar tenant automáticamente
        serializer.save(tenant=self.request.tenant)
        
    def perform_update(self, serializer):
        # Validar que el objeto pertenece al tenant
        if serializer.instance.tenant != self.request.tenant:
            raise PermissionDenied("Object does not belong to your tenant")
        serializer.save()
```

## 🛡️ Permisos Multi-Tenant

### Permission Classes
```python
# core/permissions.py
from rest_framework.permissions import BasePermission

class TenantPermission(BasePermission):
    """Validar que el usuario pertenece al tenant correcto"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Validar que el usuario pertenece al tenant del request
        return request.user.tenant == request.tenant
        
    def has_object_permission(self, request, view, obj):
        # Validar que el objeto pertenece al tenant del usuario
        return obj.tenant == request.user.tenant

class TenantOwnerPermission(BasePermission):
    """Validar que el usuario es propietario del objeto en su tenant"""
    
    def has_object_permission(self, request, view, obj):
        # Validar tenant y ownership
        return (obj.tenant == request.user.tenant and 
                hasattr(obj, 'created_by') and 
                obj.created_by == request.user)
```

## 🔧 Configuración por Tenant

### Sistema de Configuración
```python
# core/models.py
class SystemConfiguration(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    settings = models.JSONField(default=dict)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tenant', 'module']

# Ejemplo de configuraciones por módulo
CONFIGURATION_DEFAULTS = {
    'crm': {
        'appointment_duration_minutes': 60,
        'max_appointments_per_day': 10,
        'require_client_confirmation': True,
    },
    'commerce': {
        'auto_confirm_orders': False,
        'low_stock_threshold': 10,
        'tax_rate': 0.19,
    },
    'finance': {
        'require_expense_approval': True,
        'max_expense_without_approval': 1000,
        'budget_alert_threshold': 0.8,
    }
}
```

### Service para Configuración
```python
# core/services.py
class ConfigurationService:
    @staticmethod
    def get_config(tenant, module, key=None):
        try:
            config = SystemConfiguration.objects.get(
                tenant=tenant, 
                module=module
            )
            settings = config.settings
        except SystemConfiguration.DoesNotExist:
            settings = CONFIGURATION_DEFAULTS.get(module, {})
            
        if key:
            return settings.get(key)
        return settings
        
    @staticmethod
    def set_config(tenant, module, key, value, user):
        config, created = SystemConfiguration.objects.get_or_create(
            tenant=tenant,
            module=module,
            defaults={'settings': {}}
        )
        
        config.settings[key] = value
        config.updated_by = user
        config.save()
        
        return config
```

## 📊 Métricas y Monitoreo por Tenant

### Tracking de Uso
```python
# analytics/models.py
class TenantUsage(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    date = models.DateField()
    
    # Métricas de uso
    api_calls = models.IntegerField(default=0)
    storage_used_mb = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    
    # Métricas de negocio
    orders_created = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['tenant', 'date']

# Middleware para tracking
class UsageTrackingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, 'tenant') and request.tenant:
            # Incrementar contador de API calls
            self.increment_api_calls(request.tenant)
        return response
        
    def increment_api_calls(self, tenant):
        from django.utils import timezone
        today = timezone.now().date()
        
        usage, created = TenantUsage.objects.get_or_create(
            tenant=tenant,
            date=today,
            defaults={'api_calls': 0}
        )
        
        usage.api_calls += 1
        usage.save()
```

## 🚀 Escalabilidad y Performance

### Database Indexing
```python
# Índices optimizados para multi-tenancy
class Client(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'email']),  # Búsquedas por tenant + email
            models.Index(fields=['tenant', 'created_at']),  # Ordenamiento por fecha
            models.Index(fields=['tenant', 'name']),  # Búsquedas por nombre
        ]
```

### Caching por Tenant
```python
# core/cache.py
from django.core.cache import cache

class TenantCache:
    @staticmethod
    def get_key(tenant, key):
        return f"tenant_{tenant.id}_{key}"
        
    @staticmethod
    def get(tenant, key, default=None):
        cache_key = TenantCache.get_key(tenant, key)
        return cache.get(cache_key, default)
        
    @staticmethod
    def set(tenant, key, value, timeout=300):
        cache_key = TenantCache.get_key(tenant, key)
        cache.set(cache_key, value, timeout)
        
    @staticmethod
    def delete(tenant, key):
        cache_key = TenantCache.get_key(tenant, key)
        cache.delete(cache_key)
```

## 🔐 Seguridad Multi-Tenant

### Validaciones de Seguridad
```python
# core/security.py
class TenantSecurityMixin:
    def dispatch(self, request, *args, **kwargs):
        # Validar que todos los parámetros pertenecen al tenant
        self.validate_tenant_params(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
        
    def validate_tenant_params(self, request, *args, **kwargs):
        # Validar IDs en URL
        for key, value in kwargs.items():
            if key.endswith('_id') or key == 'pk':
                self.validate_object_belongs_to_tenant(key, value, request.tenant)
                
    def validate_object_belongs_to_tenant(self, param_name, object_id, tenant):
        # Implementar validación específica por modelo
        pass
```

### Audit Log Multi-Tenant
```python
# core/audit.py
class AuditLog(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'timestamp']),
            models.Index(fields=['tenant', 'user', 'timestamp']),
        ]
```

## 📋 Checklist de Implementación

### ✅ Setup Inicial
- [ ] Modelo Tenant creado
- [ ] TenantMiddleware configurado
- [ ] Context manager implementado
- [ ] BaseModel con tenant_id creado

### ✅ Managers y QuerySets
- [ ] TenantManager implementado
- [ ] Filtros automáticos funcionando
- [ ] ViewSet base multi-tenant creado
- [ ] Permisos multi-tenant implementados

### ✅ Configuración
- [ ] Sistema de configuración por tenant
- [ ] Configuraciones por defecto definidas
- [ ] Service de configuración implementado

### ✅ Seguridad
- [ ] Validaciones de tenant en todas las vistas
- [ ] Audit log implementado
- [ ] Tests de aislamiento de datos
- [ ] Validación de parámetros URL

### ✅ Performance
- [ ] Índices optimizados creados
- [ ] Sistema de cache por tenant
- [ ] Métricas de uso implementadas
- [ ] Monitoreo de performance

---
*Sistema multi-tenant diseñado para máxima seguridad, performance y escalabilidad*