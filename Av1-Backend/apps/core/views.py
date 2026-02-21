"""
Views del Core App - Arte Ideas
Solo contiene vistas compartidas entre módulos
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class CoreHealthCheckView(APIView):
    """Vista de health check para el Core App"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Health check del sistema"""
        return Response({
            'status': 'ok',
            'message': 'Arte Ideas Core App funcionando correctamente - Estructura Reorganizada',
            'modules': {
                'autenticacion': 'Autenticación - Login, logout, permisos y roles',
                'usuarios': 'Usuarios - Perfiles, actividades y gestión personal',
                'configuracion_sistema': 'Configuración - Administración, usuarios y negocio',
                'multitenancy': 'Multi-tenancy - Gestión de tenants y configuraciones específicas'
            },
            'architecture': 'Modular - Separación clara de responsabilidades'
        })