# Dashboard - Analytics Module

Módulo de Dashboard para visualización de métricas y alertas en tiempo real del sistema Arte Ideas.

## Descripción

El módulo Dashboard proporciona endpoints REST para obtener métricas, estadísticas y alertas del sistema en tiempo real. Todos los datos se calculan dinámicamente consultando la base de datos actual.

## Características

- ✅ Métricas en tiempo real (sin caché)
- ✅ Cálculo automático de porcentajes de cambio
- ✅ Sistema de alertas con prioridades
- ✅ Filtros por período (hoy, semana, mes)
- ✅ Integración con todos los módulos del sistema

## Estructura del Módulo

```
apps/analytics/dashboard/
├── __init__.py
├── admin.py                    # Configuración del admin (vacío)
├── apps.py                     # Configuración de la app
├── models.py                   # Sin modelos (solo consultas)
├── serializers.py              # Sin serializers (respuestas directas)
├── urls.py                     # Rutas de los endpoints
├── views.py                    # Lógica de negocio y cálculos
├── management/
│   └── commands/
│       └── crear_datos_prueba.py  # Comando para datos de prueba
└── README.md                   # Esta documentación
```

## Endpoints Disponibles

### 1. Resumen Completo
**GET** `/api/analytics/dashboard/resumen/`

Obtiene todos los datos del dashboard en una sola llamada.

**Respuesta:**
```json
{
  "panel_alertas_rapidas": {...},
  "estado_produccion": {...},
  "clientes": {...},
  "contratos": {...},
  "productos_mas_vendidos": [...],
  "pedidos_recientes": [...],
  "entregas_programadas_hoy": {...}
}
```

---

### 2. Panel de Alertas Rápidas
**GET** `/api/analytics/dashboard/alertas-rapidas/`

Métricas principales del negocio.

**Respuesta:**
```json
{
  "ingresos_hoy": {
    "valor": 720.0,
    "cambio_porcentaje": 22.0,
    "periodo": "Hoy"
  },
  "pedidos_activos": {
    "cantidad": 3,
    "cambio_porcentaje": 0.0,
    "detalle": "3 pendientes, 0 en proceso"
  },
  "entregas_a_tiempo": {
    "cantidad": 4,
    "atrasadas": 2,
    "cambio_porcentaje": 0.0,
    "promedio": "2h promedio"
  },
  "valor_inventario": {
    "valor": 2790.1,
    "cambio_porcentaje": 0,
    "stock_bajo": 3
  }
}
```

**Cálculos:**
- `ingresos_hoy`: Suma de pedidos completados/entregados hoy vs ayer
- `pedidos_activos`: Pedidos pendientes/en proceso/confirmados vs mes anterior
- `entregas_a_tiempo`: Órdenes de producción activas vs semana anterior
- `valor_inventario`: Suma de (precio_venta × stock_disponible) de todos los productos

---

### 3. Estado de Producción
**GET** `/api/analytics/dashboard/estado-produccion/`

Estado de las órdenes de producción.

**Respuesta:**
```json
{
  "pendientes": 2,
  "en_proceso": 2,
  "completados": 1,
  "atrasados": 0
}
```

---

### 4. Estadísticas de Clientes
**GET** `/api/analytics/dashboard/clientes-estadisticas/`

Métricas de clientes.

**Respuesta:**
```json
{
  "total": 7,
  "nuevos_este_mes": 2,
  "activos": 5,
  "inactivos": 2
}
```

**Definiciones:**
- `activos`: Clientes con pedidos en los últimos 90 días
- `nuevos_este_mes`: Clientes creados desde el día 1 del mes actual

---

### 5. Estadísticas de Contratos
**GET** `/api/analytics/dashboard/contratos-estadisticas/`

Métricas de contratos.

**Respuesta:**
```json
{
  "valor_total": 8500.0,
  "contratos_activos": 4,
  "pagos_pendientes": 2550.0,
  "por_vencer": 2
}
```

**Definiciones:**
- `por_vencer`: Contratos que vencen en los próximos 30 días

---

### 6. Productos Más Vendidos
**GET** `/api/analytics/dashboard/productos-mas-vendidos/`

Top 4 productos más vendidos.

**Respuesta:**
```json
[
  {
    "nombre": "Papel Lustre 10x15",
    "cantidad_vendida": 150,
    "ingresos": 300.0
  },
  {
    "nombre": "Revelado Digital",
    "cantidad_vendida": 100,
    "ingresos": 80.0
  }
]
```

---

### 7. Pedidos Recientes
**GET** `/api/analytics/dashboard/pedidos-recientes/`

Últimos 4 pedidos.

**Respuesta:**
```json
[
  {
    "codigo": "PED-2024-001",
    "cliente": "Juan Pérez García",
    "descripcion": "Juan Pérez García • Nota de Venta",
    "monto": 150.0,
    "estado": "completado"
  }
]
```

---

### 8. Entregas Programadas Hoy
**GET** `/api/analytics/dashboard/entregas-programadas-hoy/`

Órdenes de producción con entrega programada para hoy.

**Respuesta:**
```json
{
  "total_entregas": 2,
  "mensaje": "2 pedidos listos para entregar",
  "nota": "Todos los pedidos están listos para ser entregados hoy",
  "entregas": [
    {
      "codigo": "OP-2024-001",
      "cliente": "María López Sánchez",
      "descripcion": "Producción para PED-2024-002",
      "fecha_entrega": "2025-11-11",
      "estado": "en_proceso"
    }
  ]
}
```

---

### 9. Alertas del Sistema
**GET** `/api/analytics/dashboard/alertas/?filtro=semana`

Sistema de alertas con 3 tipos: Stock Crítico, Mantenimientos Próximos, Entregas Urgentes.

**Parámetros:**
- `filtro` (opcional): `hoy`, `semana` (default), `mes`

**Respuesta:**
```json
{
  "total_alertas": 7,
  "filtro_aplicado": "semana",
  "stock_critico": {
    "total": 3,
    "alertas": [
      {
        "nombre": "Revelador RA-4",
        "stock_actual": 5,
        "stock_minimo": 10,
        "categoria": "Minilab",
        "prioridad": "critico",
        "color": "rojo"
      }
    ]
  },
  "mantenimientos_proximos": {
    "total": 1,
    "alertas": [
      {
        "nombre": "Impresora HP LaserJet",
        "tipo_mantenimiento": "Preventivo",
        "fecha_programada": "13/11/2025",
        "dias_restantes": 2,
        "estado_texto": "2 días",
        "prioridad": "advertencia",
        "color": "naranja"
      }
    ]
  },
  "entregas_urgentes": {
    "total": 3,
    "alertas": [
      {
        "codigo": "OP-2024-002",
        "cliente": "María López Sánchez",
        "fecha_entrega": "11/11/2025",
        "dias_restantes": 0,
        "estado": "En producción",
        "descripcion": "Entrega de 4 productos de presentación",
        "prioridad": "critico",
        "color": "rojo"
      }
    ]
  }
}
```

**Prioridades:**
- `critico` (rojo): 0-1 días restantes
- `advertencia` (naranja): 2-3 días restantes
- `normal` (amarillo/verde): 4+ días restantes

---

## Autenticación

Todos los endpoints requieren autenticación JWT.

**Headers requeridos:**
```
Authorization: Bearer <access_token>
```

**Obtener token:**
```bash
POST /api/core/auth/login/
{
  "username": "admin",
  "password": "admin123"
}
```

---

## Datos de Prueba

Para crear datos de prueba, ejecuta:

```bash
python manage.py crear_datos_prueba
```

Este comando crea:
- 7 Clientes
- 5 Productos de inventario (3 con stock bajo)
- 6 Pedidos (3 completados hoy)
- 11 OrderItems (8 productos diferentes)
- 5 Órdenes de producción
- 4 Contratos
- 1 Activo con mantenimiento programado

---

## Integración con Otros Módulos

El dashboard consulta datos de:

| Módulo | Modelos Utilizados |
|--------|-------------------|
| **Commerce** | Order, OrderItem |
| **CRM** | Cliente, Contrato |
| **Operations** | OrdenProduccion, Activo, Mantenimiento |
| **Inventario** | MolduraListon, Minilab, Cuadro, etc. |

---

## Notas Técnicas

### Cálculo de Porcentajes de Cambio

Los porcentajes se calculan comparando:
- **Ingresos**: Hoy vs Ayer
- **Pedidos**: Mes actual vs Mes anterior
- **Entregas**: Esta semana vs Semana anterior

Si no hay datos históricos, el porcentaje será 0%.

### Performance

- Todas las consultas usan `select_related()` y `prefetch_related()` para optimizar queries
- Los cálculos se realizan en la base de datos usando agregaciones
- No hay caché, todos los datos son en tiempo real

### Multitenancy

Todos los endpoints filtran automáticamente por `tenant` del usuario autenticado.

---

## Troubleshooting

### Los porcentajes siempre salen en 0%
**Causa:** No hay datos históricos (ayer, mes anterior, semana anterior)
**Solución:** Agrega pedidos/órdenes de fechas anteriores

### Mantenimientos Próximos siempre en 0
**Causa:** No hay mantenimientos programados en el modelo `Mantenimiento`
**Solución:** Crea activos con mantenimientos programados desde el admin

### Stock Crítico vacío
**Causa:** Todos los productos tienen stock suficiente
**Solución:** Normal, solo aparecen productos con `stock_disponible ≤ stock_minimo`

---

## Autor

Módulo desarrollado para Arte Ideas Backend CRM
Fecha: Noviembre 2025
