"""
URLs del Módulo de Inventario - Arte Ideas Commerce
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    dashboard_inventario, metricas_api,
    MolduraListonViewSet, MolduraPrearmadaViewSet, VidrioTapaMDFViewSet,
    PaspartuViewSet, MinilabViewSet, CuadroViewSet, AnuarioViewSet,
    CorteLaserViewSet, MarcoAccesorioViewSet, HerramientaGeneralViewSet
)

app_name = 'inventario'

# Router para API REST
router = DefaultRouter()

# Categoría: Enmarcados
router.register(r'moldura-liston', MolduraListonViewSet, basename='moldura-liston')
router.register(r'moldura-prearmada', MolduraPrearmadaViewSet, basename='moldura-prearmada')
router.register(r'vidrio-tapa-mdf', VidrioTapaMDFViewSet, basename='vidrio-tapa-mdf')
router.register(r'paspartu', PaspartuViewSet, basename='paspartu')

# Categoría: Minilab
router.register(r'minilab', MinilabViewSet, basename='minilab')

# Categoría: Graduaciones
router.register(r'cuadros', CuadroViewSet, basename='cuadro')
router.register(r'anuarios', AnuarioViewSet, basename='anuario')

# Categoría: Corte Láser
router.register(r'corte-laser', CorteLaserViewSet, basename='corte-laser')

# Categoría: Accesorios
router.register(r'marco-accesorio', MarcoAccesorioViewSet, basename='marco-accesorio')
router.register(r'herramienta-general', HerramientaGeneralViewSet, basename='herramienta-general')

urlpatterns = [
    # Dashboard y métricas
    path('api/dashboard/', dashboard_inventario, name='dashboard-inventario'),
    path('api/metricas/', metricas_api, name='metricas-inventario'),
    
    # API REST para todos los modelos
    path('api/', include(router.urls)),
    
    # Rutas específicas para alertas de stock
    path('api/moldura-liston/alertas-stock/', MolduraListonViewSet.as_view({'get': 'alertas_stock'}), name='moldura-liston-alertas'),
    path('api/moldura-prearmada/alertas-stock/', MolduraPrearmadaViewSet.as_view({'get': 'alertas_stock'}), name='moldura-prearmada-alertas'),
    path('api/vidrio-tapa-mdf/alertas-stock/', VidrioTapaMDFViewSet.as_view({'get': 'alertas_stock'}), name='vidrio-tapa-mdf-alertas'),
    path('api/paspartu/alertas-stock/', PaspartuViewSet.as_view({'get': 'alertas_stock'}), name='paspartu-alertas'),
    path('api/minilab/alertas-stock/', MinilabViewSet.as_view({'get': 'alertas_stock'}), name='minilab-alertas'),
    path('api/cuadros/alertas-stock/', CuadroViewSet.as_view({'get': 'alertas_stock'}), name='cuadro-alertas'),
    path('api/anuarios/alertas-stock/', AnuarioViewSet.as_view({'get': 'alertas_stock'}), name='anuario-alertas'),
    path('api/corte-laser/alertas-stock/', CorteLaserViewSet.as_view({'get': 'alertas_stock'}), name='corte-laser-alertas'),
    path('api/marco-accesorio/alertas-stock/', MarcoAccesorioViewSet.as_view({'get': 'alertas_stock'}), name='marco-accesorio-alertas'),
    path('api/herramienta-general/alertas-stock/', HerramientaGeneralViewSet.as_view({'get': 'alertas_stock'}), name='herramienta-general-alertas'),
    
    # Rutas de compatibilidad (sin api/)
    path('dashboard/', dashboard_inventario, name='dashboard-inventario-compat'),
    path('metricas/', metricas_api, name='metricas-inventario-compat'),
    path('', include(router.urls)),
]