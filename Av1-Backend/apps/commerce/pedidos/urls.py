"""
URLs del Módulo de Pedidos - Arte Ideas Commerce
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    OrderViewSet, OrderItemViewSet, OrderPaymentViewSet, 
    OrderStatusHistoryViewSet
)

app_name = 'pedidos'

# Router para API REST
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'payments', OrderPaymentViewSet, basename='orderpayment')
router.register(r'status-history', OrderStatusHistoryViewSet, basename='orderstatushistory')

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # Rutas específicas de pedidos
    path('api/orders/estadisticas/', OrderViewSet.as_view({'get': 'estadisticas'}), name='order-estadisticas'),
    path('api/orders/resumen/', OrderViewSet.as_view({'get': 'resumen'}), name='order-resumen'),
    path('api/orders/atrasados/', OrderViewSet.as_view({'get': 'atrasados'}), name='order-atrasados'),
    path('api/orders/proximas-entregas/', OrderViewSet.as_view({'get': 'proximas_entregas'}), name='order-proximas-entregas'),
    path('api/orders/por-estado/', OrderViewSet.as_view({'get': 'por_estado'}), name='order-por-estado'),
    
    # Acciones específicas de pedidos
    path('api/orders/<int:pk>/cambiar-estado/', OrderViewSet.as_view({'post': 'cambiar_estado'}), name='order-cambiar-estado'),
    path('api/orders/<int:pk>/marcar-completado/', OrderViewSet.as_view({'post': 'marcar_completado'}), name='order-marcar-completado'),
    path('api/orders/<int:pk>/marcar-cancelado/', OrderViewSet.as_view({'post': 'marcar_cancelado'}), name='order-marcar-cancelado'),
    path('api/orders/<int:pk>/pagos/', OrderViewSet.as_view({'get': 'pagos'}), name='order-pagos'),
    path('api/orders/<int:pk>/registrar-pago/', OrderViewSet.as_view({'post': 'registrar_pago'}), name='order-registrar-pago'),
    path('api/orders/<int:pk>/historial-estados/', OrderViewSet.as_view({'get': 'historial_estados'}), name='order-historial-estados'),
    
    # Rutas de compatibilidad (sin api/)
    path('', include(router.urls)),
]