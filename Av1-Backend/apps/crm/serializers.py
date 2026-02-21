"""
Serializers del CRM App - Arte Ideas
Importaciones centralizadas de todos los módulos serializers

NOTA: Los serializers específicos están organizados en:
- clientes/serializers.py - Clientes, historial y contactos
- agenda/serializers.py - Eventos, citas y recordatorios
- contratos/serializers.py - Contratos, cláusulas y pagos

Este archivo mantiene compatibilidad con imports existentes.
"""

# Importar serializers principales para compatibilidad
from .clientes.serializers import ClienteSerializer, ClienteListSerializer
from .contratos.serializers import ContratoSerializer, ContratoListSerializer

# Mantener disponibles para compatibilidad
__all__ = [
    'ClienteSerializer', 'ClienteListSerializer',
    'ContratoSerializer', 'ContratoListSerializer'
]