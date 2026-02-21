"""
URLs del Core App - Arte Ideas
Estructura modular reorganizada según buenas prácticas
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoreHealthCheckView

app_name = 'core'

# Router para ViewSets
router = DefaultRouter()

urlpatterns = [
    # API Router
    path('', include(router.urls)),
    
    # Health Check
    path('health/', CoreHealthCheckView.as_view(), name='health_check'),
    
    # Módulo de Autenticación (login, logout, permisos)
    path('auth/', include('apps.core.autenticacion.urls')),
    
    # Módulo de Usuarios (perfiles, actividades)
    path('users/', include('apps.core.usuarios.urls')),
    
    # Módulo de Configuración del Sistema (administración, usuarios, negocio)
    path('config/', include('apps.core.configuracion_sistema.urls')),
]