"""
Este archivo se mantiene por compatibilidad pero se recomienda usar
apps.core.permissions.IsSameTenant en su lugar
"""
from apps.core.permissions import IsSameTenant

# Alias para compatibilidad con código existente
IsSameInquilino = IsSameTenant
IsSameInmobiliaria = IsSameTenant