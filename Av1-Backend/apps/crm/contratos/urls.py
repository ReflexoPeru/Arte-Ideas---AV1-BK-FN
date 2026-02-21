"""
URLs del Módulo de Contratos - Arte Ideas CRM
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContratoViewSet, ClausulaContratoViewSet, 
    PagoContratoViewSet, EstadoContratoViewSet
)

app_name = 'contratos'

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet, basename='contratos')
router.register(r'clausulas', ClausulaContratoViewSet, basename='clausulas')
router.register(r'pagos', PagoContratoViewSet, basename='pagos')
router.register(r'estados', EstadoContratoViewSet, basename='estados')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints adicionales de exportación y utilidades
    # Estos están incluidos en el ViewSet pero se documentan aquí para referencia:
    # GET /contratos/{id}/generar_pdf/ - Generar PDF del contrato
    # POST /contratos/exportar_excel/ - Exportar contratos a Excel
    # POST /contratos/exportar_pagos_excel/ - Exportar pagos a Excel
    # POST /contratos/{id}/generar_numero_contrato/ - Generar número automático
    # POST /contratos/{id}/crear_clausulas_defecto/ - Crear cláusulas por defecto
]