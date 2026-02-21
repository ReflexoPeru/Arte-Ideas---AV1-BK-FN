"""
Serializers del Operations App - Arte Ideas
Importaciones centralizadas para compatibilidad
"""

# Importar serializers de producción
from .produccion.serializers import OrdenProduccionSerializer

# Importar serializers de activos
from .activos.serializers import (
    ActivoSerializer, FinanciamientoSerializer,
    MantenimientoSerializer, RepuestoSerializer
)

# Exportar para compatibilidad
__all__ = [
    'OrdenProduccionSerializer',
    'ActivoSerializer', 'FinanciamientoSerializer',
    'MantenimientoSerializer', 'RepuestoSerializer'
]