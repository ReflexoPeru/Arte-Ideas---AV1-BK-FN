"""
Admin del CRM App - Arte Ideas
Importaciones centralizadas de todos los módulos admin

NOTA: Los admins específicos están organizados en:
- clientes/admin.py - Clientes, historial y contactos
- agenda/admin.py - Eventos, citas y recordatorios
- contratos/admin.py - Contratos, cláusulas y pagos

Este archivo mantiene compatibilidad con el admin existente.
"""
from django.contrib import admin

# Importar todos los admins para que se registren automáticamente
from .clientes import admin as clientes_admin
from .agenda import admin as agenda_admin
from .contratos import admin as contratos_admin

# Personalización del admin site para CRM
admin.site.site_header = "Arte Ideas CRM - Administración (Estructura Reorganizada)"
admin.site.site_title = "Arte Ideas CRM Admin"
admin.site.index_title = "Panel de Administración CRM - Arquitectura Modular"

# Los modelos ya están registrados en sus respectivos módulos admin
# No necesitamos registrarlos aquí nuevamente


# Los siguientes admins están comentados porque ya están registrados en sus módulos específicos
# Si necesitas personalizaciones adicionales, hazlo en los archivos correspondientes

# Configuración adicional del admin para CRM
admin.site.site_header = 'Arte Ideas CRM - Administración'
admin.site.site_title = 'Arte Ideas CRM'
admin.site.index_title = 'Panel de Administración CRM'