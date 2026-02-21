"""
Modelos del CRM App - Arte Ideas
Sistema de gestión de relaciones con clientes

NOTA: Este archivo mantiene las importaciones para compatibilidad con migraciones existentes.
Los modelos han sido reorganizados en módulos específicos:
- clientes/models.py - Clientes, historial y contactos
- agenda/models.py - Eventos, citas y recordatorios
- contratos/models.py - Contratos, cláusulas y pagos
"""

# Importar todos los modelos desde los nuevos módulos para mantener compatibilidad
from .clientes.models import Cliente, HistorialCliente, ContactoCliente
from .agenda.models import Evento, Cita, Recordatorio
from .contratos.models import Contrato, ClausulaContrato, PagoContrato, EstadoContrato

# Mantener las clases disponibles en este namespace para compatibilidad
__all__ = [
    'Cliente', 'HistorialCliente', 'ContactoCliente',
    'Evento', 'Cita', 'Recordatorio',
    'Contrato', 'ClausulaContrato', 'PagoContrato', 'EstadoContrato'
]