"""
Views del Operations App - Arte Ideas
Importaciones centralizadas para compatibilidad
"""

# Importar vistas de producción
from .produccion.views import OrdenProduccionViewSet

# Importar vistas de activos
from .activos.views import (
    dashboard_activos,
    ActivoViewSet, FinanciamientoViewSet, 
    MantenimientoViewSet, RepuestoViewSet
)

# Exportar para compatibilidad
__all__ = [
    'OrdenProduccionViewSet',
    'dashboard_activos',
    'ActivoViewSet', 'FinanciamientoViewSet', 
    'MantenimientoViewSet', 'RepuestoViewSet'
]