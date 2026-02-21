# Operations App - Arte Ideas

## Estructura Modular Reorganizada

El módulo Operations ha sido reorganizado siguiendo una arquitectura modular clara que separa las responsabilidades según las operaciones internas y gestión de recursos del estudio fotográfico.

### 📁 Estructura de Carpetas

```
apps/operations/
├── produccion/                 # Módulo de Producción
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py              # OrdenProduccion
│   ├── views.py               # ViewSets para órdenes de producción
│   ├── serializers.py         # Serializers REST API
│   ├── filters.py             # Filtros avanzados
│   ├── urls.py                # URLs del módulo
│   ├── admin.py               # Administración Django
│   ├── permissions.py         # Permisos específicos
│   ├── tests.py               # Tests del módulo
│   └── Endpoints.md           # Documentación de endpoints
├── activos/                    # Módulo de Activos
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py              # Activo, Financiamiento, Mantenimiento, Repuesto
│   ├── views.py               # ViewSets para gestión de activos
│   ├── serializers.py         # Serializers REST API
│   ├── urls.py                # URLs del módulo
│   ├── admin.py               # Administración Django
│   ├── permissions.py         # Permisos específicos
│   ├── tests.py               # Tests del módulo
│   └── forms.py               # Formularios (legacy)
├── migrations/                 # Migraciones de base de datos
├── __init__.py
├── models.py                  # Importaciones centralizadas
├── views.py                   # Importaciones centralizadas
├── urls.py                    # URLs principales
├── admin.py                   # Administración centralizada
├── serializers.py             # Serializers centralizados
├── permissions.py             # Permisos centralizados
├── tests.py                   # Tests de integración
└── README.md                  # Esta documentación
```

## 🎯 Módulos Principales

### 1. Módulo de Producción (`produccion/`)

**Responsabilidad**: Gestión de órdenes de producción y procesos internos

**Funcionalidades**:
- ✅ Gestión completa de órdenes de producción (CRUD)
- ✅ Soporte para múltiples tipos de producción (Enmarcado, Minilab, Graduación, Corte Láser, etc.)
- ✅ Gestión de estados del proceso productivo
- ✅ Asignación de operarios y seguimiento
- ✅ Integración con módulo CRM (clientes) y Commerce (pedidos)
- ✅ Dashboard con estadísticas de producción
- ✅ Filtros avanzados y búsqueda
- ✅ API REST completa con permisos por tenant

**Modelos principales**:
- `OrdenProduccion`: Órdenes de trabajo internas

**Estados de Producción**:
- Pendiente → En Proceso → Terminado → Entregado

**Tipos de Producción**:
- Enmarcado, Minilab, Graduación, Corte Láser, Edición Digital, Otro

### 2. Módulo de Activos (`activos/`)

**Responsabilidad**: Gestión de activos, mantenimientos y recursos

**Funcionalidades**:
- ✅ Gestión completa de activos fijos
- ✅ Cálculo automático de depreciación
- ✅ Gestión de financiamientos y leasing
- ✅ Programación y seguimiento de mantenimientos
- ✅ Control de repuestos e insumos
- ✅ Alertas automáticas de mantenimiento y stock
- ✅ Dashboard de métricas de activos
- ✅ API REST moderna con todas las funcionalidades

**Modelos principales**:
- `Activo`: Activos fijos del estudio
- `Financiamiento`: Financiamientos y leasing
- `Mantenimiento`: Mantenimientos preventivos y correctivos
- `Repuesto`: Repuestos e insumos

**Categorías de Activos**:
- Impresoras, Equipo de Oficina, Maquinaria, Herramientas, Vehículos

**Tipos de Mantenimiento**:
- Preventivo, Correctivo, Emergencia

## 🔗 Integración y Compatibilidad

### Importaciones Centralizadas
Los archivos principales (`models.py`, `views.py`, `admin.py`, `urls.py`) mantienen importaciones centralizadas para garantizar compatibilidad con:
- ✅ Migraciones existentes de Django
- ✅ Código legacy que importe desde el módulo principal
- ✅ APIs externas que dependan de las rutas originales

### URLs y API
```python
# URLs principales
/operations/produccion/        # Módulo de producción
/operations/activos/           # Módulo de activos

# APIs REST
/operations/produccion/api/    # API de producción
/operations/activos/api/       # API de activos

# Compatibilidad
/operations/                   # Alias para producción (legacy)
```

## 📊 Funcionalidades Destacadas

### Producción
- **Estados avanzados**: Pendiente, En Proceso, Terminado, Entregado
- **Tipos especializados**: Enmarcado, Minilab, Graduación, Corte Láser
- **Asignación de operarios**: Control por roles y permisos
- **Integración completa**: Con pedidos de Commerce y clientes de CRM
- **Dashboard**: Estadísticas en tiempo real por estado

### Activos
- **Depreciación automática**: Cálculo en tiempo real del valor actual
- **Gestión financiera**: Financiamientos, cuotas y saldos pendientes
- **Mantenimientos**: Programación automática y alertas
- **Control de repuestos**: Alertas de stock bajo y gestión de inventario
- **Reportes**: Depreciación, mantenimientos vencidos, valor de activos

## 🚀 Funcionalidades Nuevas Implementadas

### API REST Moderna para Activos
- **Antes**: Solo vistas tradicionales de Django con formularios
- **Ahora**: API REST completa con ViewSets, serializers y permisos

### Nuevos Endpoints de Activos:
```python
# Dashboard y métricas
GET /operations/activos/api/dashboard/

# Gestión de activos
GET/POST /operations/activos/api/activos/
GET /operations/activos/api/activos/por-categoria/
GET /operations/activos/api/activos/depreciacion-report/

# Gestión de mantenimientos
GET/POST /operations/activos/api/mantenimientos/
GET /operations/activos/api/mantenimientos/proximos/
GET /operations/activos/api/mantenimientos/vencidos/
POST /operations/activos/api/mantenimientos/{id}/completar/

# Gestión de repuestos
GET/POST /operations/activos/api/repuestos/
GET /operations/activos/api/repuestos/alertas-stock/
POST /operations/activos/api/repuestos/{id}/actualizar-stock/
```

### Mejoras en Producción:
- ✅ Filtrado automático por tenant
- ✅ Permisos granulares por rol
- ✅ Dashboard con estadísticas
- ✅ Integración mejorada con Commerce y CRM

## 🔧 Archivos Implementados

**Nuevos Archivos Creados:**
- ✅ `activos/serializers.py` - Serializers REST API para activos
- ✅ `activos/permissions.py` - Permisos específicos por módulo
- ✅ `produccion/apps.py` - Configuración del módulo producción
- ✅ `produccion/tests.py` - Tests específicos de producción
- ✅ `activos/tests.py` - Tests específicos de activos (actualizado)
- ✅ Archivos centralizados de compatibilidad

**Archivos Actualizados:**
- ✅ `activos/views.py` - Modernizado a API REST completa
- ✅ `activos/urls.py` - URLs REST API organizadas
- ✅ `activos/apps.py` - Configuración corregida
- ✅ `urls.py` - URLs principales reorganizadas

## 🎯 Próximos Pasos

1. **Migraciones**: Ejecutar migraciones para aplicar cambios en modelos
2. **Tests**: Ejecutar tests para validar funcionalidad
3. **Frontend**: Adaptar interfaces para usar las nuevas APIs REST
4. **Documentación**: Completar documentación de endpoints
5. **Optimización**: Implementar cache y optimizaciones de consultas

## 🔧 Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations operations

# Aplicar migraciones
python manage.py migrate

# Ejecutar tests
python manage.py test apps.operations

# Ejecutar tests específicos
python manage.py test apps.operations.produccion
python manage.py test apps.operations.activos
```

---

**Nota**: Esta reorganización mantiene total compatibilidad con el código existente mientras proporciona una estructura más clara, APIs REST modernas y funcionalidades avanzadas para la gestión completa de operaciones internas y recursos del estudio fotográfico.