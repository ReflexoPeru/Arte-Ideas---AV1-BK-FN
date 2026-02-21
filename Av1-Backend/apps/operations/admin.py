"""
Administración del Operations App - Arte Ideas
Importaciones centralizadas para compatibilidad
"""

# Importar administraciones de producción
from .produccion.admin import OrdenProduccionAdmin

# Importar administraciones de activos
from .activos.admin import (
    ActivoAdmin, FinanciamientoAdmin, 
    MantenimientoAdmin, RepuestoAdmin
)

# Las administraciones ya están registradas en sus módulos específicos
# Este archivo mantiene compatibilidad con importaciones centralizadas