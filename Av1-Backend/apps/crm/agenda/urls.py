from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventoViewSet, CitaViewSet, RecordatorioViewSet, AgendaDashboardViewSet,
    AgendaDashboardView, ProximosEventosView, EventosHoyView, CitasPendientesView,
    ProximosEventosDemoView, demo_proximos_eventos
)

app_name = 'agenda'

router = DefaultRouter()
router.register(r'eventos', EventoViewSet, basename='eventos')
router.register(r'citas', CitaViewSet, basename='citas')
router.register(r'recordatorios', RecordatorioViewSet, basename='recordatorios')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', AgendaDashboardView.as_view(), name='agenda-dashboard'),
    path('proximos-eventos/', ProximosEventosView.as_view(), name='proximos-eventos'),
    path('proximos-eventos-demo/', ProximosEventosDemoView.as_view(), name='proximos-eventos-demo'),
    path('demo/', demo_proximos_eventos, name='demo-proximos-eventos'),
    path('eventos-hoy/', EventosHoyView.as_view(), name='eventos-hoy'),
    path('citas-pendientes/', CitasPendientesView.as_view(), name='citas-pendientes'),
]