"""
URLs del Módulo de Producción - Arte Ideas Operations
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrdenProduccionViewSet

app_name = 'produccion'

# Router para API REST
router = DefaultRouter()
router.register(r'ordenes', OrdenProduccionViewSet, basename='orden-produccion')

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # Rutas específicas de producción
    path('api/ordenes/dashboard/', OrdenProduccionViewSet.as_view({'get': 'dashboard'}), name='ordenes-dashboard'),
    path('api/ordenes/por-estado/', OrdenProduccionViewSet.as_view({'get': 'por_estado'}), name='ordenes-por-estado'),
    path('api/ordenes/por-tipo/', OrdenProduccionViewSet.as_view({'get': 'por_tipo'}), name='ordenes-por-tipo'),
    path('api/ordenes/por-operario/', OrdenProduccionViewSet.as_view({'get': 'por_operario'}), name='ordenes-por-operario'),
    path('api/ordenes/vencidas/', OrdenProduccionViewSet.as_view({'get': 'vencidas'}), name='ordenes-vencidas'),
    path('api/ordenes/proximas/', OrdenProduccionViewSet.as_view({'get': 'proximas'}), name='ordenes-proximas'),
    path('api/ordenes/resumen-produccion/', OrdenProduccionViewSet.as_view({'get': 'resumen_produccion'}), name='ordenes-resumen'),
    
    # Acciones específicas de órdenes
    path('api/ordenes/<int:pk>/cambiar-estado/', OrdenProduccionViewSet.as_view({'post': 'cambiar_estado'}), name='orden-cambiar-estado'),
    path('api/ordenes/<int:pk>/marcar-completado/', OrdenProduccionViewSet.as_view({'post': 'marcar_completado'}), name='orden-marcar-completado'),
    
    # Rutas de compatibilidad (sin api/)
    path('', include(router.urls)),
]