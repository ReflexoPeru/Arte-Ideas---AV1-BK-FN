"""
URLs del Operations App - Arte Ideas
Configuración de rutas para operaciones internas y recursos
"""
from django.urls import path, include

app_name = 'operations'

urlpatterns = [
    # Módulo de Producción
    path('produccion/', include('apps.operations.produccion.urls')),
    
    # Módulo de Activos
    path('activos/', include('apps.operations.activos.urls')),
    
    # Rutas de compatibilidad
    path('', include('apps.operations.produccion.urls')),  # Mantener compatibilidad con producción
]