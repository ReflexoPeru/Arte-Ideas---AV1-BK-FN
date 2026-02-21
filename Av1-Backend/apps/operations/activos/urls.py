"""
URLs del Módulo de Activos - Arte Ideas Operations
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    dashboard_activos,
    ActivoViewSet, FinanciamientoViewSet, 
    MantenimientoViewSet, RepuestoViewSet
)

app_name = 'activos'

# Router para API REST
router = DefaultRouter()
router.register(r'activos', ActivoViewSet, basename='activo')
router.register(r'financiamientos', FinanciamientoViewSet, basename='financiamiento')
router.register(r'mantenimientos', MantenimientoViewSet, basename='mantenimiento')
router.register(r'repuestos', RepuestoViewSet, basename='repuesto')

urlpatterns = [
    # Dashboard y métricas
    path('api/dashboard/', dashboard_activos, name='dashboard-activos'),
    
    # API REST para todos los modelos
    path('api/', include(router.urls)),
    
    # Rutas específicas para activos
    path('api/activos/por-categoria/', ActivoViewSet.as_view({'get': 'por_categoria'}), name='activos-por-categoria'),
    path('api/activos/depreciacion-report/', ActivoViewSet.as_view({'get': 'depreciacion_report'}), name='activos-depreciacion'),
    path('api/activos/mantenimientos-pendientes/', ActivoViewSet.as_view({'get': 'mantenimientos_pendientes'}), name='activos-mantenimientos-pendientes'),
    
    # Rutas específicas para financiamientos
    path('api/financiamientos/resumen-financiero/', FinanciamientoViewSet.as_view({'get': 'resumen_financiero'}), name='financiamientos-resumen'),
    path('api/financiamientos/<int:pk>/marcar-pagado/', FinanciamientoViewSet.as_view({'post': 'marcar_pagado'}), name='financiamiento-marcar-pagado'),
    
    # Rutas específicas para mantenimientos
    path('api/mantenimientos/proximos/', MantenimientoViewSet.as_view({'get': 'proximos'}), name='mantenimientos-proximos'),
    path('api/mantenimientos/vencidos/', MantenimientoViewSet.as_view({'get': 'vencidos'}), name='mantenimientos-vencidos'),
    path('api/mantenimientos/<int:pk>/completar/', MantenimientoViewSet.as_view({'post': 'completar'}), name='mantenimiento-completar'),
    
    # Rutas específicas para repuestos
    path('api/repuestos/alertas-stock/', RepuestoViewSet.as_view({'get': 'alertas_stock'}), name='repuestos-alertas'),
    path('api/repuestos/sin-stock/', RepuestoViewSet.as_view({'get': 'sin_stock'}), name='repuestos-sin-stock'),
    path('api/repuestos/<int:pk>/actualizar-stock/', RepuestoViewSet.as_view({'post': 'actualizar_stock'}), name='repuesto-actualizar-stock'),
    path('api/repuestos/resumen-inventario/', RepuestoViewSet.as_view({'get': 'resumen_inventario'}), name='repuestos-resumen'),
    
    # Rutas de compatibilidad (sin api/)
    path('', include(router.urls)),
]
