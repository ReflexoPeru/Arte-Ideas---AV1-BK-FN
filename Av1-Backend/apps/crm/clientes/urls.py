"""
URLs del Módulo de Clientes - Arte Ideas CRM
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, HistorialClienteViewSet, ContactoClienteViewSet

app_name = 'clientes'

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'historial', HistorialClienteViewSet, basename='historial')
router.register(r'contactos', ContactoClienteViewSet, basename='contactos')

urlpatterns = [
    path('', include(router.urls)),
]