# CRM App - Arte Ideas

## Estructura Reorganizada (Arquitectura Modular)

La carpeta `crm/` ha sido reorganizada siguiendo las buenas prácticas de Django y un patrón de arquitectura modular para mejorar la gestión de relaciones con clientes en estudios fotográficos.

### 📁 Estructura de Carpetas

```
apps/crm/
├── clientes/               # Módulo de Clientes
│   ├── __init__.py
│   ├── models.py          # Cliente, HistorialCliente, ContactoCliente
│   ├── views.py           # ClienteViewSet, HistorialClienteViewSet, etc.
│   ├── serializers.py     # ClienteSerializer, HistorialClienteSerializer, etc.
│   ├── urls.py            # URLs de gestión de clientes
│   ├── admin.py           # Admin para clientes y contactos
│   └── tests.py           # Tests del módulo
│
├── agenda/                 # Módulo de Agenda
│   ├── __init__.py
│   ├── models.py          # Evento, Cita, Recordatorio
│   ├── views.py           # EventoViewSet, CitaViewSet, etc.
│   ├── serializers.py     # EventoSerializer, CitaSerializer, etc.
│   ├── urls.py            # URLs de agenda y citas
│   ├── admin.py           # Admin para eventos y citas
│   ├── filters.py         # Filtros personalizados
│   ├── signals.py         # Signals de agenda
│   └── tests.py           # Tests del módulo
│
├── contratos/              # Módulo de Contratos
│   ├── __init__.py
│   ├── models.py          # Contrato, ClausulaContrato, PagoContrato, EstadoContrato
│   ├── views.py           # ContratoViewSet, PagoContratoViewSet, etc.
│   ├── serializers.py     # ContratoSerializer, PagoContratoSerializer, etc.
│   ├── urls.py            # URLs de contratos y pagos
│   ├── admin.py           # Admin para contratos y pagos
│   └── tests.py           # Tests del módulo
│
├── migrations/            # Migraciones de Django
├── __init__.py
├── models.py             # Importaciones para compatibilidad
├── views.py              # Vista de health check
├── urls.py               # URLs principales reorganizadas
├── admin.py              # Importaciones centralizadas de admins
├── serializers.py        # Importaciones centralizadas de serializers
├── tests.py              # Tests generales
└── README.md             # Esta documentación
```

### 🎯 Responsabilidades por Módulo

#### 1. **clientes/** - Gestión de Clientes
- **Propósito**: Gestión completa de clientes: particulares, colegios y empresas
- **Modelos**: `Cliente`, `HistorialCliente`, `ContactoCliente`
- **Funcionalidades**:
  - Gestión de clientes por tipo (particular, colegio, empresa)
  - Historial de interacciones con clientes
  - Contactos adicionales para empresas y colegios
  - Estadísticas de clientes
  - Activación/desactivación de clientes

#### 2. **agenda/** - Gestión de Agenda
- **Propósito**: Eventos, citas y recordatorios
- **Modelos**: `Evento`, `Cita`, `Recordatorio`
- **Funcionalidades**:
  - Gestión de eventos y citas
  - Recordatorios automáticos
  - Dashboard de agenda
  - Verificación de disponibilidad
  - Seguimiento de citas y resultados

#### 3. **contratos/** - Gestión de Contratos
- **Propósito**: Contratos, cláusulas, pagos y estados
- **Modelos**: `Contrato`, `ClausulaContrato`, `PagoContrato`, `EstadoContrato`
- **Funcionalidades**:
  - Gestión completa de contratos
  - Cláusulas personalizables
  - Registro de pagos y adelantos
  - Historial de cambios de estado
  - Control de vencimientos
  - Estadísticas financieras

### 🔗 URLs Reorganizadas

```python
# apps/crm/urls.py
urlpatterns = [
    path('health/', CRMHealthCheckView.as_view(), name='health_check'),
    path('clientes/', include('apps.crm.clientes.urls')),    # /api/crm/clientes/
    path('agenda/', include('apps.crm.agenda.urls')),        # /api/crm/agenda/
    path('contratos/', include('apps.crm.contratos.urls')),  # /api/crm/contratos/
]
```

### 🔄 Compatibilidad con Migraciones

El archivo `models.py` principal mantiene las importaciones de todos los modelos para asegurar compatibilidad:

```python
# Importar todos los modelos desde los nuevos módulos
from .clientes.models import Cliente, HistorialCliente, ContactoCliente
from .agenda.models import Evento, Cita, Recordatorio
from .contratos.models import Contrato, ClausulaContrato, PagoContrato, EstadoContrato
```

### 🧪 Testing

Cada módulo tiene su propio archivo `tests.py` con tests específicos:

- `clientes/tests.py` - Tests de clientes, historial y contactos
- `agenda/tests.py` - Tests de eventos, citas y recordatorios
- `contratos/tests.py` - Tests de contratos, pagos y estados

### 📊 Admin Interface

Los admins están organizados por módulo:

- **Clientes**: Gestión visual de clientes con indicadores por tipo
- **Agenda**: Dashboard de eventos con estados y recordatorios
- **Contratos**: Control de contratos con indicadores de vencimiento y pagos

### 🔧 Funcionalidades Principales

#### Módulo Clientes
- ✅ Gestión de 3 tipos de clientes (particular, colegio, empresa)
- ✅ Historial completo de interacciones
- ✅ Contactos adicionales para empresas/colegios
- ✅ Estadísticas y reportes de clientes
- ✅ Búsqueda y filtros avanzados

#### Módulo Agenda
- ✅ Eventos con diferentes tipos y prioridades
- ✅ Citas con seguimiento de resultados
- ✅ Recordatorios automáticos
- ✅ Dashboard de agenda personalizado
- ✅ Verificación de disponibilidad

#### Módulo Contratos
- ✅ Contratos con múltiples tipos de servicio
- ✅ Cláusulas personalizables
- ✅ Sistema de pagos y adelantos
- ✅ Historial de cambios de estado
- ✅ Control de vencimientos
- ✅ Estadísticas financieras

### 🚀 Beneficios de la Nueva Estructura

1. **Separación Clara**: Cada módulo tiene responsabilidades específicas
2. **Escalabilidad**: Fácil agregar nuevas funcionalidades CRM
3. **Mantenibilidad**: Código organizado y fácil de mantener
4. **Testing**: Tests específicos por funcionalidad
5. **Multi-tenancy**: Soporte completo para múltiples estudios
6. **APIs RESTful**: Endpoints organizados y documentados

### 📋 Endpoints Principales

#### Clientes
- `GET /api/crm/clientes/clientes/` - Listar clientes
- `POST /api/crm/clientes/clientes/` - Crear cliente
- `GET /api/crm/clientes/clientes/{id}/historial/` - Historial del cliente
- `POST /api/crm/clientes/clientes/{id}/agregar_interaccion/` - Agregar interacción
- `GET /api/crm/clientes/clientes/estadisticas/` - Estadísticas de clientes

#### Agenda
- `GET /api/crm/agenda/eventos/` - Listar eventos
- `POST /api/crm/agenda/eventos/` - Crear evento
- `GET /api/crm/agenda/eventos/eventos_hoy/` - Eventos de hoy
- `POST /api/crm/agenda/eventos/verificar_disponibilidad/` - Verificar disponibilidad
- `GET /api/crm/agenda/citas/` - Listar citas

#### Contratos
- `GET /api/crm/contratos/contratos/` - Listar contratos
- `POST /api/crm/contratos/contratos/` - Crear contrato
- `POST /api/crm/contratos/contratos/{id}/registrar_pago/` - Registrar pago
- `GET /api/crm/contratos/contratos/estadisticas/` - Estadísticas de contratos
- `GET /api/crm/contratos/contratos/vencidos/` - Contratos vencidos

### 🔄 Migración de Datos

La reorganización mantiene compatibilidad total:
- Los modelos siguen siendo accesibles desde `apps.crm.models`
- Las migraciones existentes funcionan sin cambios
- Los endpoints principales mantienen compatibilidad

### 📝 Notas Importantes

- **Multi-tenancy**: Todos los módulos respetan el sistema de tenants
- **Permisos**: Control de acceso por tenant y rol de usuario
- **Validaciones**: Validaciones específicas por tipo de cliente/contrato
- **Historial**: Registro completo de actividades y cambios
- **Estadísticas**: Dashboards y reportes por módulo

Esta reorganización establece una base sólida para la gestión completa de relaciones con clientes en estudios fotográficos, manteniendo la funcionalidad existente mientras proporciona una estructura escalable y mantenible.