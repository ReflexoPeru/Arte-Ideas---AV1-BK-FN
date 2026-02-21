"""
Views del CRM App - Arte Ideas
Solo contiene vistas compartidas entre módulos
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class CRMHealthCheckView(APIView):
    """Vista de health check para el CRM App"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Health check del sistema CRM"""
        return Response({
            'status': 'ok',
            'message': 'Arte Ideas CRM App funcionando correctamente - Estructura Reorganizada',
            'modules': {
                'clientes': 'Clientes - Gestión completa de clientes: particulares, colegios y empresas',
                'agenda': 'Agenda - Eventos, citas y recordatorios',
                'contratos': 'Contratos - Contratos, cláusulas, pagos y estados'
            },
            'architecture': 'Modular - Separación clara de responsabilidades CRM'
        })