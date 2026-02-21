"""
URLs del CRM App - Arte Ideas
Estructura modular reorganizada según buenas prácticas
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CRMHealthCheckView

app_name = 'crm'

# Router para ViewSets principales (compatibilidad)
router = DefaultRouter()

urlpatterns = [
    # API Router principal
    path('', include(router.urls)),
    
    # Health Check
    path('health/', CRMHealthCheckView.as_view(), name='health_check'),
    
    # Módulo de Clientes (gestión completa de clientes)
    path('clientes/', include('apps.crm.clientes.urls')),
    
    # Módulo de Agenda (eventos, citas y recordatorios)
    path('agenda/', include('apps.crm.agenda.urls')),
    
    # Módulo de Contratos (contratos, cláusulas y pagos)
    path('contratos/', include('apps.crm.contratos.urls')),
    
    # Compatibilidad con rutas anteriores
    path('contracts/', include('apps.crm.contratos.urls')),  # Mantener por compatibilidad
]