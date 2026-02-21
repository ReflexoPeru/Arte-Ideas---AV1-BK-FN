"""
URLs del Analytics App - Arte Ideas
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from .views import ReportViewSet

app_name = 'analytics'

# Router para ViewSets (para compatibilidad con otras rutas si las hay)
router = DefaultRouter()

# Vistas basadas en clase que usan el ViewSet
class CategoriasView(APIView):
    """Vista para listar categorías de reportes"""
    permission_classes = ReportViewSet.permission_classes
    
    def get(self, request):
        viewset = ReportViewSet()
        # Inicializar el request correctamente
        viewset.request = request
        viewset.format_kwarg = getattr(request, 'format', None)
        # Llamar al método del ViewSet
        return viewset.categorias(request)

class TodosView(APIView):
    """Vista para obtener todos los reportes"""
    permission_classes = ReportViewSet.permission_classes
    
    def get(self, request):
        viewset = ReportViewSet()
        viewset.request = request
        viewset.format_kwarg = getattr(request, 'format', None)
        return viewset.todos(request)

class ObtenerReporteView(APIView):
    """Vista para obtener un reporte específico"""
    permission_classes = ReportViewSet.permission_classes
    
    def get(self, request, categoria):
        viewset = ReportViewSet()
        viewset.request = request
        viewset.format_kwarg = getattr(request, 'format', None)
        return viewset.obtener_reporte(request, categoria=categoria)

class ExportarExcelView(APIView):
    """Vista para exportar reporte a Excel"""
    permission_classes = ReportViewSet.permission_classes
    
    def get(self, request, categoria):
        viewset = ReportViewSet()
        viewset.request = request
        viewset.format_kwarg = getattr(request, 'format', None)
        return viewset.exportar_excel(request, categoria=categoria)

class ExportarPdfView(APIView):
    """Vista para exportar reporte a PDF"""
    permission_classes = ReportViewSet.permission_classes
    
    def get(self, request, categoria):
        viewset = ReportViewSet()
        viewset.request = request
        viewset.format_kwarg = getattr(request, 'format', None)
        return viewset.exportar_pdf(request, categoria=categoria)

urlpatterns = [
    # Rutas de reportes - definidas manualmente para soportar parámetros dinámicos
    path('reportes/categorias/', CategoriasView.as_view(), name='reportes-categorias'),
    path('reportes/todos/', TodosView.as_view(), name='reportes-todos'),
    path('reportes/<str:categoria>/', ObtenerReporteView.as_view(), name='reportes-obtener'),
    path('reportes/<str:categoria>/exportar/excel/', ExportarExcelView.as_view(), name='reportes-exportar-excel'),
    path('reportes/<str:categoria>/exportar/pdf/', ExportarPdfView.as_view(), name='reportes-exportar-pdf'),
]