"""
Middleware de Multi-tenancy - Arte Ideas
Middleware para gestión de tenants en las requests
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware para identificar y validar el tenant en cada request
    """
    
    def process_request(self, request):
        """
        Procesar request para identificar tenant
        """
        # Obtener tenant desde headers o subdomain
        tenant_slug = None
        
        # Opción 1: Desde header X-Tenant
        if 'HTTP_X_TENANT' in request.META:
            tenant_slug = request.META['HTTP_X_TENANT']
        
        # Opción 2: Desde subdomain (ej: estudio1.arteideas.com)
        elif hasattr(request, 'get_host'):
            host = request.get_host()
            if '.' in host:
                subdomain = host.split('.')[0]
                if subdomain != 'www' and subdomain != 'api':
                    tenant_slug = subdomain
        
        # Opción 3: Desde parámetro en URL
        if not tenant_slug and 'tenant' in request.GET:
            tenant_slug = request.GET['tenant']
        
        # Buscar tenant si se encontró slug
        if tenant_slug:
            try:
                tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
                request.tenant = tenant
            except Tenant.DoesNotExist:
                request.tenant = None
        else:
            request.tenant = None
        
        return None
    
    def process_response(self, request, response):
        """
        Procesar response para agregar headers de tenant
        """
        if hasattr(request, 'tenant') and request.tenant:
            response['X-Tenant'] = request.tenant.slug
            response['X-Tenant-Name'] = request.tenant.name
        
        return response


class TenantValidationMiddleware(MiddlewareMixin):
    """
    Middleware para validar que el usuario pertenezca al tenant correcto
    """
    
    def process_request(self, request):
        """
        Validar que el usuario autenticado pertenezca al tenant de la request
        """
        # Solo validar en requests autenticadas
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Super admin puede acceder a cualquier tenant
        if request.user.role == 'super_admin':
            return None
        
        # Validar que el usuario pertenezca al tenant
        if hasattr(request, 'tenant') and request.tenant:
            if request.user.tenant != request.tenant:
                return JsonResponse({
                    'error': 'Usuario no autorizado para este tenant',
                    'code': 'TENANT_MISMATCH'
                }, status=403)
        
        return None