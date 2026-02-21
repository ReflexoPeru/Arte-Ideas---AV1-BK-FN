"""
URLs del Commerce App - Arte Ideas
Configuración de rutas para operaciones comerciales y stock
"""
from django.urls import path, include

app_name = 'commerce'

urlpatterns = [
    # Módulo de Pedidos
    path('pedidos/', include('apps.commerce.pedidos.urls')),
    
    # Módulo de Inventario
    path('inventario/', include('apps.commerce.inventario.urls')),
    
    # Rutas de compatibilidad (mantener por migraciones)
    path('orders/', include('apps.commerce.pedidos.urls')),
    path('inventory/', include('apps.commerce.inventario.urls')),
]