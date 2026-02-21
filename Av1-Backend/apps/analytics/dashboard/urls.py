"""
Dashboard URLs - Analytics App
"""
from django.urls import path
from .views import (
    PanelAlertasRapidasView,
    EstadoProduccionView,
    ClientesEstadisticasView,
    ContratosEstadisticasView,
    ProductosMasVendidosView,
    PedidosRecientesView,
    EntregasProgramadasHoyView,
    DashboardResumenView,
    AlertasView
)

app_name = 'dashboard'

urlpatterns = [
    # Endpoint principal - Resumen completo del dashboard
    path('resumen/', DashboardResumenView.as_view(), name='dashboard-resumen'),
    
    # Alertas dinámicas del sistema
    path('alertas/', AlertasView.as_view(), name='alertas'),
    
    # Endpoints individuales
    path('alertas-rapidas/', PanelAlertasRapidasView.as_view(), name='alertas-rapidas'),
    path('estado-produccion/', EstadoProduccionView.as_view(), name='estado-produccion'),
    path('clientes-estadisticas/', ClientesEstadisticasView.as_view(), name='clientes-estadisticas'),
    path('contratos-estadisticas/', ContratosEstadisticasView.as_view(), name='contratos-estadisticas'),
    path('productos-mas-vendidos/', ProductosMasVendidosView.as_view(), name='productos-mas-vendidos'),
    path('pedidos-recientes/', PedidosRecientesView.as_view(), name='pedidos-recientes'),
    path('entregas-programadas-hoy/', EntregasProgramadasHoyView.as_view(), name='entregas-programadas-hoy'),
]
