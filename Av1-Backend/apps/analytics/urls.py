"""
URLs del Analytics App - Arte Ideas
"""
from django.urls import path, include

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('dashboard/', include('apps.analytics.dashboard.urls')),
    
    # Incluir URLs de Reportes
    path('', include('apps.analytics.Reportes.urls')),
]

