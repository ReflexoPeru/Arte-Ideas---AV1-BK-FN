"""
Analytics Views - Arte Ideas
Vistas para generación y visualización de reportes
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json
import io
from decimal import Decimal

from .services import (
    VentasReportService, InventarioReportService, ProduccionReportService,
    ClientesReportService, FinancieroReportService, ContratosReportService
)
from .serializers import ReportSerializer
from .exporters import ExcelExporter, PDFExporter


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de reportes
    """
    permission_classes = [IsAuthenticated]
    
    # Mapeo de categorías a servicios
    CATEGORIAS = {
        'ventas': {
            'service': VentasReportService,
            'titulo': 'Reporte de Ventas',
            'nombre_archivo': 'Reporte_Ventas'
        },
        'inventario': {
            'service': InventarioReportService,
            'titulo': 'Reporte de Inventario',
            'nombre_archivo': 'Reporte_Inventario'
        },
        'produccion': {
            'service': ProduccionReportService,
            'titulo': 'Reporte de Producción',
            'nombre_archivo': 'Reporte_Produccion'
        },
        'clientes': {
            'service': ClientesReportService,
            'titulo': 'Reporte de Clientes',
            'nombre_archivo': 'Reporte_Clientes'
        },
        'financiero': {
            'service': FinancieroReportService,
            'titulo': 'Reporte Financiero',
            'nombre_archivo': 'Reporte_Financiero'
        },
        'contratos': {
            'service': ContratosReportService,
            'titulo': 'Reporte de Contratos',
            'nombre_archivo': 'Reporte_Contratos'
        },
    }
    
    def get_tenant(self):
        """Obtener tenant del usuario autenticado"""
        user = self.request.user
        
        # Si el usuario tiene tenant asignado, usarlo
        if hasattr(user, 'tenant') and user.tenant:
            return user.tenant
        
        # Si es super_admin y no tiene tenant, usar el primero disponible (útil para desarrollo/testing)
        if hasattr(user, 'role') and user.role == 'super_admin':
            from apps.core.multitenancy.models import Tenant
            first_tenant = Tenant.objects.filter(is_active=True).first()
            if first_tenant:
                return first_tenant
        
        # Si no hay tenant disponible, devolver None
        return None
    
    def parse_dates(self, request):
        """Parsear fechas desde los parámetros de la request"""
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            except ValueError:
                fecha_inicio = (timezone.now() - timedelta(days=30)).date()
        else:
            fecha_inicio = (timezone.now() - timedelta(days=30)).date()
        
        if fecha_fin:
            try:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            except ValueError:
                fecha_fin = timezone.now().date()
        else:
            fecha_fin = timezone.now().date()
        
        return fecha_inicio, fecha_fin
    
    @action(detail=False, methods=['get'])
    def categorias(self, request):
        """Listar todas las categorías de reportes disponibles"""
        categorias = [
            {
                'codigo': codigo,
                'nombre': info['titulo'],
                'descripcion': f'Reporte de {info["titulo"]}'
            }
            for codigo, info in self.CATEGORIAS.items()
        ]
        return Response(categorias)
    
    def obtener_reporte(self, request, categoria=None):
        """
        Obtener reporte de una categoría específica
        Parámetros: categoria, fecha_inicio, fecha_fin
        """
        categoria = categoria.lower()
        
        if categoria not in self.CATEGORIAS:
            return Response(
                {'error': f'Categoría "{categoria}" no válida. Categorías disponibles: {", ".join(self.CATEGORIAS.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {
                    'error': 'Usuario no tiene tenant asignado',
                    'mensaje': 'Por favor, asigna un tenant a tu usuario. Puedes usar: python manage.py setup_tenant --username tu_usuario --create-tenant',
                    'ayuda': {
                        'listar_tenants': 'python manage.py setup_tenant --list-tenants',
                        'listar_usuarios': 'python manage.py setup_tenant --list-users',
                        'crear_tenant': 'python manage.py setup_tenant --username tu_usuario --create-tenant',
                        'asignar_tenant': 'python manage.py setup_tenant --username tu_usuario --tenant-id 1'
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        fecha_inicio, fecha_fin = self.parse_dates(request)
        
        # Obtener servicio correspondiente
        service_class = self.CATEGORIAS[categoria]['service']
        service = service_class(tenant, fecha_inicio, fecha_fin)
        
        # Generar métricas y detalle
        metricas = service.get_metrics()
        detalle = service.get_detalle()
        
        # Formatear respuesta
        reporte = {
            'categoria': categoria,
            'titulo': self.CATEGORIAS[categoria]['titulo'],
            'periodo_inicio': fecha_inicio.isoformat(),
            'periodo_fin': fecha_fin.isoformat(),
            'metricas': metricas,
            'detalle': detalle,
            'fecha_generacion': timezone.now().isoformat(),
        }
        
        serializer = ReportSerializer(reporte)
        return Response(serializer.data)
    
    def exportar_excel(self, request, categoria=None):
        """
        Exportar reporte a Excel
        Parámetros: categoria, fecha_inicio, fecha_fin, rango (visible/completo)
        """
        categoria = categoria.lower()
        
        if categoria not in self.CATEGORIAS:
            return Response(
                {'error': f'Categoría "{categoria}" no válida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {
                    'error': 'Usuario no tiene tenant asignado',
                    'mensaje': 'Por favor, asigna un tenant a tu usuario. Puedes usar: python manage.py setup_tenant --username tu_usuario --create-tenant',
                    'ayuda': {
                        'listar_tenants': 'python manage.py setup_tenant --list-tenants',
                        'listar_usuarios': 'python manage.py setup_tenant --list-users',
                        'crear_tenant': 'python manage.py setup_tenant --username tu_usuario --create-tenant',
                        'asignar_tenant': 'python manage.py setup_tenant --username tu_usuario --tenant-id 1'
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        fecha_inicio, fecha_fin = self.parse_dates(request)
        rango = request.query_params.get('rango', 'visible').lower()
        
        # Obtener datos del reporte
        service_class = self.CATEGORIAS[categoria]['service']
        service = service_class(tenant, fecha_inicio, fecha_fin)
        
        metricas = service.get_metrics()
        detalle = service.get_detalle()
        
        # Generar Excel
        exporter = ExcelExporter()
        nombre_archivo = self.CATEGORIAS[categoria]['nombre_archivo']
        titulo = self.CATEGORIAS[categoria]['titulo']
        
        try:
            excel_file = exporter.export_report(
                titulo=titulo,
                metricas=metricas,
                detalle=detalle,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                categoria=categoria
            )
            
            # Generar nombre de archivo con fecha
            fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{nombre_archivo}_{fecha_str}.xlsx"
            
            response = HttpResponse(
                excel_file,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al exportar a Excel: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def exportar_pdf(self, request, categoria=None):
        """
        Exportar reporte a PDF
        Parámetros: categoria, fecha_inicio, fecha_fin, rango (visible/completo)
        """
        categoria = categoria.lower()
        
        if categoria not in self.CATEGORIAS:
            return Response(
                {'error': f'Categoría "{categoria}" no válida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {
                    'error': 'Usuario no tiene tenant asignado',
                    'mensaje': 'Por favor, asigna un tenant a tu usuario. Puedes usar: python manage.py setup_tenant --username tu_usuario --create-tenant',
                    'ayuda': {
                        'listar_tenants': 'python manage.py setup_tenant --list-tenants',
                        'listar_usuarios': 'python manage.py setup_tenant --list-users',
                        'crear_tenant': 'python manage.py setup_tenant --username tu_usuario --create-tenant',
                        'asignar_tenant': 'python manage.py setup_tenant --username tu_usuario --tenant-id 1'
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        fecha_inicio, fecha_fin = self.parse_dates(request)
        rango = request.query_params.get('rango', 'visible').lower()
        
        # Obtener datos del reporte
        service_class = self.CATEGORIAS[categoria]['service']
        service = service_class(tenant, fecha_inicio, fecha_fin)
        
        metricas = service.get_metrics()
        detalle = service.get_detalle()
        
        # Generar PDF
        exporter = PDFExporter()
        nombre_archivo = self.CATEGORIAS[categoria]['nombre_archivo']
        titulo = self.CATEGORIAS[categoria]['titulo']
        
        try:
            pdf_file = exporter.export_report(
                titulo=titulo,
                metricas=metricas,
                detalle=detalle,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                categoria=categoria
            )
            
            # Generar nombre de archivo con fecha
            fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{nombre_archivo}_{fecha_str}.pdf"
            
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al exportar a PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def todos(self, request):
        """
        Obtener todos los reportes de todas las categorías
        Útil para dashboard general
        """
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {
                    'error': 'Usuario no tiene tenant asignado',
                    'mensaje': 'Por favor, asigna un tenant a tu usuario. Puedes usar: python manage.py setup_tenant --username tu_usuario --create-tenant',
                    'ayuda': {
                        'listar_tenants': 'python manage.py setup_tenant --list-tenants',
                        'listar_usuarios': 'python manage.py setup_tenant --list-users',
                        'crear_tenant': 'python manage.py setup_tenant --username tu_usuario --create-tenant',
                        'asignar_tenant': 'python manage.py setup_tenant --username tu_usuario --tenant-id 1'
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        fecha_inicio, fecha_fin = self.parse_dates(request)
        
        reportes = {}
        
        for categoria, info in self.CATEGORIAS.items():
            service_class = info['service']
            service = service_class(tenant, fecha_inicio, fecha_fin)
            
            metricas = service.get_metrics()
            detalle = service.get_detalle()
            
            reportes[categoria] = {
                'titulo': info['titulo'],
                'periodo_inicio': fecha_inicio.isoformat(),
                'periodo_fin': fecha_fin.isoformat(),
                'metricas': metricas,
                'detalle': detalle[:10],  # Limitar detalle para no sobrecargar
                'total_registros': len(detalle),
            }
        
        return Response(reportes)
