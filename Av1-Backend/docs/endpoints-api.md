# 📋 Documentación de Endpoints API - Arte Ideas

Esta documentación contiene todos los endpoints disponibles en el sistema Arte Ideas, organizados por módulos y con ejemplos de respuestas exitosas (200 OK).

## 🚀 Índice de Módulos

1. [CORE - Módulo Principal](#core---módulo-principal)
2. [CRM - Gestión de Clientes](#crm---gestión-de-clientes)
3. [COMMERCE - Comercio e Inventario](#commerce---comercio-e-inventario)
4. [OPERATIONS - Operaciones](#operations---operaciones)
5. [FINANCE - Finanzas](#finance---finanzas)
6. [ANALYTICS - Analíticas](#analytics---analíticas)
7. [ADMIN - Panel de Administración](#admin---panel-de-administración)

---

## 🔧 CORE - Módulo Principal

**Base URL:** `/api/core/`

### Health Check
- `GET /api/core/health/` - Verificación de salud del sistema

### Autenticación
- `POST /api/core/auth/login/` - Obtener tokens JWT (access y refresh)
- `POST /api/core/auth/refresh/` - Renovar token de acceso usando refresh
- `POST /api/core/auth/logout/` - Cierre de sesión (blacklist de refresh)

### Usuarios
- `GET /api/core/users/profile/` - Perfil de usuario
- `GET /api/core/users/profile/statistics/` - Estadísticas del perfil
- `GET /api/core/users/profile/completion/` - Completitud del perfil
- `GET /api/core/users/profile/activity/` - Actividad del perfil
- `POST /api/core/users/change-password/` - Cambiar contraseña
- `POST /api/core/users/change-email/` - Cambiar email

### Configuración del Sistema
- `GET /api/core/config/business/` - Configuración del negocio
- `GET /api/core/config/users/` - Gestión de usuarios
- `GET /api/core/config/users/{user_id}/` - Detalle de usuario
- `GET /api/core/config/roles/` - Lista de roles
- `GET /api/core/config/permissions/` - Lista de permisos
- `GET /api/core/config/permissions/{role}/` - Permisos por rol
- `GET /api/core/config/tenants/` - Gestión de tenants
- `GET /api/core/config/tenants/{tenant_id}/users/` - Usuarios por tenant

---

## 📊 CRM - Gestión de Clientes

**Base URL:** `/api/crm/`

### Health Check
- `GET /api/crm/health/` - Verificación de salud del CRM

### Clientes
**Base:** `/api/crm/clientes/`
- `GET /api/crm/clientes/clientes/` - Listar clientes
- `POST /api/crm/clientes/clientes/` - Crear cliente
- `GET /api/crm/clientes/clientes/{id}/` - Detalle cliente
- `PUT /api/crm/clientes/clientes/{id}/` - Actualizar cliente
- `DELETE /api/crm/clientes/clientes/{id}/` - Eliminar cliente
- `GET /api/crm/clientes/historial/` - Historial de clientes
- `GET /api/crm/clientes/contactos/` - Contactos de clientes

### Agenda
**Base:** `/api/crm/agenda/`
- `GET /api/crm/agenda/eventos/` - Listar eventos
- `GET /api/crm/agenda/citas/` - Listar citas
- `GET /api/crm/agenda/recordatorios/` - Listar recordatorios
- `GET /api/crm/agenda/dashboard/` - Dashboard de agenda
- `GET /api/crm/agenda/proximos-eventos/` - Próximos eventos
- `GET /api/crm/agenda/proximos-eventos-demo/` - Demo de próximos eventos
- `GET /api/crm/agenda/demo/` - Demo de eventos
- `GET /api/crm/agenda/eventos-hoy/` - Eventos de hoy
- `GET /api/crm/agenda/citas-pendientes/` - Citas pendientes

### Contratos
**Base:** `/api/crm/contratos/`
- `GET /api/crm/contratos/contratos/` - Listar contratos
- `GET /api/crm/contratos/clausulas/` - Listar cláusulas
- `GET /api/crm/contratos/pagos/` - Listar pagos
- `GET /api/crm/contratos/estados/` - Listar estados

---

## 🛒 COMMERCE - Comercio e Inventario

**Base URL:** `/api/commerce/`

### Pedidos
**Base:** `/api/commerce/pedidos/`

**CRUD básico:**
- `GET /api/commerce/pedidos/api/orders/` - Listar pedidos
- `POST /api/commerce/pedidos/api/orders/` - Crear pedido
- `GET /api/commerce/pedidos/api/order-items/` - Items de pedidos
- `GET /api/commerce/pedidos/api/payments/` - Pagos de pedidos
- `GET /api/commerce/pedidos/api/status-history/` - Historial de estados

**Reportes y estadísticas:**
- `GET /api/commerce/pedidos/api/orders/estadisticas/` - Estadísticas de pedidos
- `GET /api/commerce/pedidos/api/orders/resumen/` - Resumen de pedidos
- `GET /api/commerce/pedidos/api/orders/atrasados/` - Pedidos atrasados
- `GET /api/commerce/pedidos/api/orders/proximas-entregas/` - Próximas entregas
- `GET /api/commerce/pedidos/api/orders/por-estado/` - Pedidos por estado

**Acciones de pedidos:**
- `POST /api/commerce/pedidos/api/orders/{id}/cambiar-estado/` - Cambiar estado
- `POST /api/commerce/pedidos/api/orders/{id}/marcar-completado/` - Marcar completado
- `POST /api/commerce/pedidos/api/orders/{id}/marcar-cancelado/` - Marcar cancelado
- `GET /api/commerce/pedidos/api/orders/{id}/pagos/` - Ver pagos del pedido
- `POST /api/commerce/pedidos/api/orders/{id}/registrar-pago/` - Registrar pago
- `GET /api/commerce/pedidos/api/orders/{id}/historial-estados/` - Historial de estados

### Inventario
**Base:** `/api/commerce/inventario/`

**Dashboard y métricas:**
- `GET /api/commerce/inventario/api/dashboard/` - Dashboard de inventario
- `GET /api/commerce/inventario/api/metricas/` - Métricas de inventario

**Categorías de inventario:**
- `GET /api/commerce/inventario/api/moldura-liston/` - Moldura listón
- `GET /api/commerce/inventario/api/moldura-prearmada/` - Moldura prearmada
- `GET /api/commerce/inventario/api/vidrio-tapa-mdf/` - Vidrio/tapa MDF
- `GET /api/commerce/inventario/api/paspartu/` - Paspartú
- `GET /api/commerce/inventario/api/minilab/` - Minilab
- `GET /api/commerce/inventario/api/cuadros/` - Cuadros
- `GET /api/commerce/inventario/api/anuarios/` - Anuarios
- `GET /api/commerce/inventario/api/corte-laser/` - Corte láser
- `GET /api/commerce/inventario/api/marco-accesorio/` - Accesorios de marco
- `GET /api/commerce/inventario/api/herramienta-general/` - Herramientas generales

**Alertas de stock:**
- `GET /api/commerce/inventario/api/moldura-liston/alertas-stock/`
- `GET /api/commerce/inventario/api/moldura-prearmada/alertas-stock/`
- `GET /api/commerce/inventario/api/vidrio-tapa-mdf/alertas-stock/`
- `GET /api/commerce/inventario/api/paspartu/alertas-stock/`
- `GET /api/commerce/inventario/api/minilab/alertas-stock/`
- `GET /api/commerce/inventario/api/cuadros/alertas-stock/`
- `GET /api/commerce/inventario/api/anuarios/alertas-stock/`
- `GET /api/commerce/inventario/api/corte-laser/alertas-stock/`
- `GET /api/commerce/inventario/api/marco-accesorio/alertas-stock/`
- `GET /api/commerce/inventario/api/herramienta-general/alertas-stock/`

---

## ⚙️ OPERATIONS - Operaciones

**Base URL:** `/api/operations/`

### Activos
**Base:** `/api/operations/activos/`

**Dashboard y métricas:**
- `GET /api/operations/activos/api/dashboard/` - Dashboard de activos

**Gestión de activos:**
- `GET /api/operations/activos/api/activos/` - Listar activos
- `GET /api/operations/activos/api/financiamientos/` - Listar financiamientos
- `GET /api/operations/activos/api/mantenimientos/` - Listar mantenimientos
- `GET /api/operations/activos/api/repuestos/` - Listar repuestos

**Reportes específicos:**
- `GET /api/operations/activos/api/activos/por-categoria/` - Activos por categoría
- `GET /api/operations/activos/api/activos/depreciacion-report/` - Reporte de depreciación
- `GET /api/operations/activos/api/activos/mantenimientos-pendientes/` - Mantenimientos pendientes

- `GET /api/operations/activos/api/financiamientos/resumen-financiero/` - Resumen financiero
- `POST /api/operations/activos/api/financiamientos/{id}/marcar-pagado/` - Marcar como pagado

- `GET /api/operations/activos/api/mantenimientos/proximos/` - Próximos mantenimientos
- `GET /api/operations/activos/api/mantenimientos/vencidos/` - Mantenimientos vencidos
- `POST /api/operations/activos/api/mantenimientos/{id}/completar/` - Completar mantenimiento

- `GET /api/operations/activos/api/repuestos/alertas-stock/` - Alertas de stock
- `GET /api/operations/activos/api/repuestos/sin-stock/` - Repuestos sin stock
- `POST /api/operations/activos/api/repuestos/{id}/actualizar-stock/` - Actualizar stock
- `GET /api/operations/activos/api/repuestos/resumen-inventario/` - Resumen de inventario

### Producción
**Base:** `/api/operations/produccion/`
- `GET /api/operations/produccion/api/ordenes/` - Órdenes de producción
- `GET /api/operations/produccion/api/ordenes/dashboard/` - Dashboard de órdenes
- `GET /api/operations/produccion/api/ordenes/por-estado/` - Órdenes por estado
- `GET /api/operations/produccion/api/ordenes/por-tipo/` - Órdenes por tipo
- `GET /api/operations/produccion/api/ordenes/por-operario/` - Órdenes por operario
- `GET /api/operations/produccion/api/ordenes/vencidas/` - Órdenes vencidas
- `GET /api/operations/produccion/api/ordenes/proximas/` - Próximas órdenes
- `GET /api/operations/produccion/api/ordenes/resumen-produccion/` - Resumen de producción
- `POST /api/operations/produccion/api/ordenes/{id}/cambiar-estado/` - Cambiar estado
- `POST /api/operations/produccion/api/ordenes/{id}/marcar-completado/` - Marcar completado

---

## 💰 FINANCE - Finanzas

**Base URL:** `/api/finance/`
- `GET /api/finance/` - Endpoints de finanzas (router vacío actualmente)

---

## 📈 ANALYTICS - Analíticas

**Base URL:** `/api/analytics/`

### Reportes
**Base:** `/api/analytics/reportes/`

#### Listar Categorías de Reportes
- **Endpoint:** `GET /api/analytics/reportes/categorias/`
- **Descripción:** Obtiene todas las categorías de reportes disponibles
- **Autenticación:** Requerida (JWT Token)
- **Parámetros:** Ninguno
- **Respuesta exitosa (200):**
```json
[
    {
        "codigo": "ventas",
        "nombre": "Reporte de Ventas",
        "descripcion": "Reporte de Reporte de Ventas"
    },
    {
        "codigo": "inventario",
        "nombre": "Reporte de Inventario",
        "descripcion": "Reporte de Reporte de Inventario"
    },
    {
        "codigo": "produccion",
        "nombre": "Reporte de Producción",
        "descripcion": "Reporte de Reporte de Producción"
    },
    {
        "codigo": "clientes",
        "nombre": "Reporte de Clientes",
        "descripcion": "Reporte de Reporte de Clientes"
    },
    {
        "codigo": "financiero",
        "nombre": "Reporte Financiero",
        "descripcion": "Reporte de Reporte Financiero"
    },
    {
        "codigo": "contratos",
        "nombre": "Reporte de Contratos",
        "descripcion": "Reporte de Reporte de Contratos"
    }
]
```

#### Obtener Todos los Reportes
- **Endpoint:** `GET /api/analytics/reportes/todos/`
- **Descripción:** Obtiene todos los reportes de todas las categorías (útil para dashboard)
- **Autenticación:** Requerida (JWT Token)
- **Parámetros Query:**
  - `fecha_inicio` (opcional): Fecha de inicio en formato `YYYY-MM-DD` (default: 30 días atrás)
  - `fecha_fin` (opcional): Fecha de fin en formato `YYYY-MM-DD` (default: hoy)
- **Ejemplo de URL:** `/api/analytics/reportes/todos/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31`
- **Respuesta exitosa (200):**
```json
{
    "ventas": {
        "titulo": "Reporte de Ventas",
        "periodo_inicio": "2024-01-01",
        "periodo_fin": "2024-01-31",
        "metricas": {
            "total_ventas": 150000.50,
            "total_pedidos": 45,
            "promedio_venta": 3333.34,
            "tasa_completitud": 85.50,
            "total_pagado": 120000.00,
            "saldo_pendiente": 30000.50
        },
        "detalle": [...],
        "total_registros": 45
    },
    "inventario": {...},
    "produccion": {...},
    "clientes": {...},
    "financiero": {...},
    "contratos": {...}
}
```

#### Obtener Reporte Específico
- **Endpoint:** `GET /api/analytics/reportes/{categoria}/`
- **Descripción:** Obtiene el reporte de una categoría específica
- **Autenticación:** Requerida (JWT Token)
- **Parámetros URL:**
  - `categoria` (requerido): Una de las siguientes categorías:
    - `ventas`
    - `inventario`
    - `produccion`
    - `clientes`
    - `financiero`
    - `contratos`
- **Parámetros Query:**
  - `fecha_inicio` (opcional): Fecha de inicio en formato `YYYY-MM-DD` (default: 30 días atrás)
  - `fecha_fin` (opcional): Fecha de fin en formato `YYYY-MM-DD` (default: hoy)
- **Ejemplo de URL:** `/api/analytics/reportes/ventas/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31`
- **Respuesta exitosa (200) - Reporte de Ventas:**
```json
{
    "categoria": "ventas",
    "titulo": "Reporte de Ventas",
    "periodo_inicio": "2024-01-01",
    "periodo_fin": "2024-01-31",
    "metricas": {
        "total_ventas": 150000.50,
        "total_pedidos": 45,
        "promedio_venta": 3333.34,
        "tasa_completitud": 85.50,
        "total_pagado": 120000.00,
        "saldo_pendiente": 30000.50
    },
    "detalle": [
        {
            "id": 1,
            "numero_pedido": "PED-2024-001",
            "cliente": "Juan Pérez",
            "fecha": "2024-01-15",
            "tipo_documento": "Nota de Venta",
            "total": 5000.00,
            "pagado": 5000.00,
            "saldo": 0.00,
            "estado": "Completado",
            "estado_pago": "Pagado Completo"
        }
    ],
    "fecha_generacion": "2024-01-31T10:30:00Z"
}
```

#### Exportar Reporte a Excel
- **Endpoint:** `GET /api/analytics/reportes/{categoria}/exportar/excel/`
- **Descripción:** Exporta el reporte de una categoría específica a formato Excel (.xlsx)
- **Autenticación:** Requerida (JWT Token)
- **Parámetros URL:**
  - `categoria` (requerido): Una de las categorías disponibles (ventas, inventario, produccion, clientes, financiero, contratos)
- **Parámetros Query:**
  - `fecha_inicio` (opcional): Fecha de inicio en formato `YYYY-MM-DD` (default: 30 días atrás)
  - `fecha_fin` (opcional): Fecha de fin en formato `YYYY-MM-DD` (default: hoy)
  - `rango` (opcional): `visible` o `completo` (default: `visible`)
- **Ejemplo de URL:** `/api/analytics/reportes/ventas/exportar/excel/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31&rango=completo`
- **Respuesta exitosa (200):** Archivo Excel descargable
- **Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Headers de respuesta:**
  - `Content-Disposition: attachment; filename="Reporte_Ventas_20240131_103000.xlsx"`

#### Exportar Reporte a PDF
- **Endpoint:** `GET /api/analytics/reportes/{categoria}/exportar/pdf/`
- **Descripción:** Exporta el reporte de una categoría específica a formato PDF
- **Autenticación:** Requerida (JWT Token)
- **Parámetros URL:**
  - `categoria` (requerido): Una de las categorías disponibles (ventas, inventario, produccion, clientes, financiero, contratos)
- **Parámetros Query:**
  - `fecha_inicio` (opcional): Fecha de inicio en formato `YYYY-MM-DD` (default: 30 días atrás)
  - `fecha_fin` (opcional): Fecha de fin en formato `YYYY-MM-DD` (default: hoy)
  - `rango` (opcional): `visible` o `completo` (default: `visible`)
- **Ejemplo de URL:** `/api/analytics/reportes/ventas/exportar/pdf/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31&rango=completo`
- **Respuesta exitosa (200):** Archivo PDF descargable
- **Content-Type:** `application/pdf`
- **Headers de respuesta:**
  - `Content-Disposition: attachment; filename="Reporte_Ventas_20240131_103000.pdf"`

### Ejemplos de Respuestas por Categoría

#### Reporte de Inventario
```json
{
    "categoria": "inventario",
    "titulo": "Reporte de Inventario",
    "periodo_inicio": "2024-01-01",
    "periodo_fin": "2024-01-31",
    "metricas": {
        "total_productos": 150,
        "total_stock": 5000,
        "total_valor_inventario": 2500000.00,
        "productos_bajo_stock": 15,
        "productos_ok_stock": 135
    },
    "detalle": [
        {
            "id": 1,
            "categoria": "Moldura Listón",
            "nombre": "Moldura Listón 2x4",
            "codigo": "ML-001",
            "stock_disponible": 50,
            "stock_minimo": 20,
            "costo_unitario": 15.50,
            "precio_venta": 25.00,
            "valor_total": 775.00,
            "alerta_stock": false,
            "proveedor": "Proveedor XYZ"
        }
    ]
}
```

#### Reporte de Producción
```json
{
    "categoria": "produccion",
    "titulo": "Reporte de Producción",
    "periodo_inicio": "2024-01-01",
    "periodo_fin": "2024-01-31",
    "metricas": {
        "total_ordenes": 30,
        "ordenes_completadas": 25,
        "ordenes_en_proceso": 3,
        "ordenes_pendientes": 2,
        "ordenes_vencidas": 1,
        "tiempo_promedio_horas": 4.5,
        "tasa_completitud": 83.33
    },
    "detalle": [
        {
            "id": 1,
            "numero_op": "OP-2024-001",
            "pedido": "PED-2024-001",
            "cliente": "Juan Pérez",
            "tipo": "Enmarcado",
            "estado": "Terminado",
            "prioridad": "Alta",
            "fecha_estimada": "2024-01-15",
            "fecha_finalizacion": "2024-01-14",
            "operario": "María González",
            "tiempo_estimado": 5.0,
            "tiempo_real": 4.5,
            "vencida": false
        }
    ]
}
```

#### Reporte de Clientes
```json
{
    "categoria": "clientes",
    "titulo": "Reporte de Clientes",
    "periodo_inicio": "2024-01-01",
    "periodo_fin": "2024-01-31",
    "metricas": {
        "total_clientes": 100,
        "clientes_particulares": 60,
        "clientes_colegios": 30,
        "clientes_empresas": 10,
        "clientes_nuevos": 15
    },
    "detalle": [
        {
            "id": 1,
            "tipo_cliente": "Particular",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "nombre_completo": "Juan Pérez",
            "email": "juan@example.com",
            "telefono": "987654321",
            "dni": "12345678",
            "total_pedidos": 5,
            "total_ventas": 25000.00,
            "fecha_registro": "2023-06-15"
        }
    ]
}
```

#### Reporte Financiero
```json
{
    "categoria": "financiero",
    "titulo": "Reporte Financiero",
    "periodo_inicio": "2024-01-01",
    "periodo_fin": "2024-01-31",
    "metricas": {
        "total_ingresos": 150000.00,
        "total_pagado": 120000.00,
        "total_pagos_recibidos": 120000.00,
        "saldo_pendiente": 30000.00,
        "igv_recaudado": 22881.36,
        "ingresos_netos": 127118.64
    },
    "detalle": [
        {
            "id": 1,
            "fecha": "2024-01-15",
            "numero_pedido": "PED-2024-001",
            "cliente": "Juan Pérez",
            "monto": 5000.00,
            "metodo_pago": "Efectivo",
            "numero_referencia": "",
            "notas": ""
        }
    ]
}
```

#### Reporte de Contratos
```json
{
    "categoria": "contratos",
    "titulo": "Reporte de Contratos",
    "periodo_inicio": "2024-01-01",
    "periodo_fin": "2024-01-31",
    "metricas": {
        "total_contratos": 10,
        "total_monto": 50000.00,
        "total_adelantos": 15000.00,
        "total_saldo_pendiente": 35000.00,
        "contratos_activos": 8,
        "contratos_completados": 2
    },
    "detalle": [
        {
            "id": 1,
            "numero_contrato": "CONT-2024-001",
            "titulo": "Contrato de Fotografía Anual",
            "cliente": "Colegio San Juan",
            "tipo_servicio": "Fotografía Escolar",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31",
            "monto_total": 10000.00,
            "adelanto": 3000.00,
            "saldo_pendiente": 7000.00,
            "estado": "Activo",
            "porcentaje_adelanto": 30.00
        }
    ]
}
```

### Errores Comunes

#### Error 400 - Categoría no válida
```json
{
    "error": "Categoría \"categoria_invalida\" no válida. Categorías disponibles: ventas, inventario, produccion, clientes, financiero, contratos"
}
```

#### Error 403 - Sin tenant asignado
```json
{
    "error": "Usuario no tiene tenant asignado"
}
```

#### Error 500 - Error al exportar
```json
{
    "error": "Error al exportar a Excel: Se requiere openpyxl o xlsxwriter para exportar a Excel. Instale con: pip install openpyxl"
}
```

---

## 🔑 ADMIN - Panel de Administración Django

- `GET /admin/` - Panel de administración Django

---

## 📄 Ejemplos de Respuestas 200 OK

### Health Check (/api/core/health/)
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "database": "connected",
    "services": {
        "authentication": "operational",
        "database": "operational"
    }
}
```

### Listar Clientes (/api/crm/clientes/clientes/)
```json
[
    {
        "id": 1,
        "nombre": "Juan Pérez",
        "email": "juan@example.com",
        "telefono": "+56912345678",
        "direccion": "Calle Principal 123",
        "fecha_registro": "2024-01-01T00:00:00Z",
        "estado": "activo"
    }
]
```

### Dashboard de Agenda (/api/crm/agenda/dashboard/)
```json
{
    "total_eventos": 25,
    "eventos_hoy": 5,
    "citas_pendientes": 8,
    "recordatorios_activos": 12,
    "proximos_eventos": [
        {
            "id": 1,
            "titulo": "Reunión con cliente",
            "fecha": "2024-01-16T15:00:00Z",
            "tipo": "cita"
        }
    ]
}
```

### Dashboard de Inventario (/api/commerce/inventario/api/dashboard/)
```json
{
    "total_productos": 150,
    "productos_bajo_stock": 15,
    "productos_sin_stock": 3,
    "valor_total_inventario": 2500000,
    "categorias": {
        "moldura_liston": 45,
        "moldura_prearmada": 30,
        "vidrio": 25
    }
}
```

### Órdenes de Producción (/api/operations/produccion/api/ordenes/)
```json
[
    {
        "id": 1,
        "numero_orden": "OP-2024-001",
        "tipo_orden": "enmarcado",
        "estado": "en_proceso",
        "fecha_creacion": "2024-01-10T08:00:00Z",
        "fecha_entrega_estimada": "2024-01-20T17:00:00Z",
        "prioridad": "alta"
    }
]
```

### Alertas de Stock (/api/commerce/inventario/api/moldura-liston/alertas-stock/)
```json
[
    {
        "id": 1,
        "nombre": "Moldura Listón 2x4",
        "codigo": "ML-001",
        "stock_actual": 5,
        "stock_minimo": 10,
        "estado": "bajo_stock"
    }
]
```

---

## 📝 Notas Importantes

### Métodos HTTP
- **GET**: Obtener datos/listados
- **POST**: Crear nuevos recursos o ejecutar acciones
- **PUT/PATCH**: Actualizar recursos existentes
- **DELETE**: Eliminar recursos

### Respuestas Exitosas
- **200 OK**: Solicitud exitosa con datos
- **201 Created**: Recurso creado exitosamente
- **204 No Content**: Solicitud exitosa sin contenido de respuesta

### Autenticación
Algunos endpoints pueden requerir autenticación. Asegúrate de incluir los tokens de autenticación necesarios en los headers de tus peticiones.

### Versionado
La API actualmente no tiene versionado explícito. Todas las rutas están en su versión actual.

### Rutas de Compatibilidad
Varios módulos incluyen rutas de compatibilidad para mantener retrocompatibilidad con versiones anteriores del sistema.

---

## 🚀 Guía de Uso en Postman

### Configuración Inicial

#### 1. Variables de Entorno
Crea un entorno en Postman con las siguientes variables:

| Variable | Valor Ejemplo | Descripción |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000` | URL base del servidor |
| `access_token` | `eyJ0eXAiOiJKV1QiLCJhbGc...` | Token JWT de acceso |
| `refresh_token` | `eyJ0eXAiOiJKV1QiLCJhbGc...` | Token JWT de refresh |

#### 2. Autenticación
Todos los endpoints de Analytics requieren autenticación JWT.

**Paso 1: Obtener Token de Acceso**
```
POST {{base_url}}/api/core/auth/login/
Content-Type: application/json

{
    "username": "tu_usuario",
    "password": "tu_contraseña"
}
```

**Respuesta:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Paso 2: Configurar Header de Autorización**
En cada solicitud a los endpoints de Analytics, agrega el header:
```
Authorization: Bearer {{access_token}}
```

#### 3. Headers Comunes
Para todas las solicitudes JSON:
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

### Ejemplos de Solicitudes en Postman

#### Listar Categorías de Reportes
```
GET {{base_url}}/api/analytics/reportes/categorias/
Headers:
  Authorization: Bearer {{access_token}}
```

#### Obtener Reporte de Ventas
```
GET {{base_url}}/api/analytics/reportes/ventas/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31
Headers:
  Authorization: Bearer {{access_token}}
```

#### Obtener Todos los Reportes
```
GET {{base_url}}/api/analytics/reportes/todos/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31
Headers:
  Authorization: Bearer {{access_token}}
```

#### Exportar Reporte a Excel
```
GET {{base_url}}/api/analytics/reportes/ventas/exportar/excel/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31&rango=completo
Headers:
  Authorization: Bearer {{access_token}}
```

**Nota:** Para exportaciones, asegúrate de seleccionar "Send and Download" en Postman para descargar el archivo.

#### Exportar Reporte a PDF
```
GET {{base_url}}/api/analytics/reportes/ventas/exportar/pdf/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31&rango=completo
Headers:
  Authorization: Bearer {{access_token}}
```

### Colección de Postman

Para facilitar el uso, puedes crear una colección de Postman con los siguientes endpoints:

#### Estructura de Carpeta Recomendada:
```
📁 Arte Ideas API
  📁 Auth
    📄 Login
    📄 Refresh Token
    📄 Logout
  📁 Analytics
    📁 Reportes
      📄 Listar Categorías
      📄 Obtener Todos los Reportes
      📄 Obtener Reporte de Ventas
      📄 Obtener Reporte de Inventario
      📄 Obtener Reporte de Producción
      📄 Obtener Reporte de Clientes
      📄 Obtener Reporte Financiero
      📄 Obtener Reporte de Contratos
      📄 Exportar Ventas a Excel
      📄 Exportar Ventas a PDF
      📄 Exportar Inventario a Excel
      📄 Exportar Inventario a PDF
      ... (más exportaciones)
```

### Scripts de Postman (Tests)

#### Script para guardar automáticamente el token de acceso:
```javascript
// En el Test tab de la request de Login
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
    console.log("Tokens guardados exitosamente");
}
```

#### Script para refrescar el token automáticamente:
```javascript
// Pre-request Script para endpoints que requieren autenticación
const refreshToken = pm.environment.get("refresh_token");

if (refreshToken) {
    pm.sendRequest({
        url: pm.environment.get("base_url") + '/api/core/auth/refresh/',
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                refresh: refreshToken
            })
        }
    }, function (err, res) {
        if (res.code === 200) {
            var jsonData = res.json();
            pm.environment.set("access_token", jsonData.access);
            console.log("Token refrescado automáticamente");
        }
    });
}
```

### Parámetros de Fecha

#### Formato de Fecha
Todas las fechas deben estar en formato `YYYY-MM-DD`:
- ✅ Correcto: `2024-01-31`
- ❌ Incorrecto: `31/01/2024`, `2024-31-01`, `01-31-2024`

#### Valores por Defecto
Si no se proporcionan las fechas:
- `fecha_inicio`: 30 días antes de la fecha actual
- `fecha_fin`: Fecha actual

#### Ejemplos de URLs con Fechas:
```
# Reporte del último mes
{{base_url}}/api/analytics/reportes/ventas/

# Reporte de un rango específico
{{base_url}}/api/analytics/reportes/ventas/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31

# Reporte del último trimestre
{{base_url}}/api/analytics/reportes/ventas/?fecha_inicio=2024-01-01&fecha_fin=2024-03-31
```

### Categorías Disponibles

Las siguientes categorías están disponibles para los endpoints de reportes:

| Categoría | Código | Descripción |
|-----------|--------|-------------|
| Ventas | `ventas` | Reporte de ventas y pedidos |
| Inventario | `inventario` | Reporte de inventario y stock |
| Producción | `produccion` | Reporte de órdenes de producción |
| Clientes | `clientes` | Reporte de clientes |
| Financiero | `financiero` | Reporte financiero y pagos |
| Contratos | `contratos` | Reporte de contratos |

### Manejo de Errores

#### Error 401 - No autenticado
```json
{
    "detail": "Las credenciales de autenticación no se proveyeron."
}
```
**Solución:** Verifica que el header `Authorization: Bearer {{access_token}}` esté incluido.

#### Error 403 - Sin tenant asignado
```json
{
    "error": "Usuario no tiene tenant asignado",
    "mensaje": "Por favor, asigna un tenant a tu usuario. Puedes usar: python manage.py setup_tenant --username tu_usuario --create-tenant",
    "ayuda": {
        "listar_tenants": "python manage.py setup_tenant --list-tenants",
        "listar_usuarios": "python manage.py setup_tenant --list-users",
        "crear_tenant": "python manage.py setup_tenant --username tu_usuario --create-tenant",
        "asignar_tenant": "python manage.py setup_tenant --username tu_usuario --tenant-id 1"
    }
}
```
**Solución:** El usuario debe tener un tenant asignado en la base de datos.

**Pasos para resolver:**

1. **Listar usuarios sin tenant:**
   ```bash
   python manage.py setup_tenant --list-users
   ```

2. **Crear y asignar un tenant a tu usuario:**
   ```bash
   python manage.py setup_tenant --username tu_usuario --create-tenant
   ```

3. **O asignar un tenant existente:**
   ```bash
   # Primero listar tenants disponibles
   python manage.py setup_tenant --list-tenants
   
   # Luego asignar un tenant específico
   python manage.py setup_tenant --username tu_usuario --tenant-id 1
   ```

**Nota para Super Admins:**
Si eres un super admin y no tienes tenant asignado, el sistema intentará usar el primer tenant disponible automáticamente (útil para desarrollo/testing). Sin embargo, es recomendable asignar un tenant explícitamente.

#### Error 400 - Categoría no válida
```json
{
    "error": "Categoría \"categoria_invalida\" no válida. Categorías disponibles: ventas, inventario, produccion, clientes, financiero, contratos"
}
```
**Solución:** Verifica que la categoría en la URL sea una de las categorías disponibles.

#### Error 500 - Error al exportar
```json
{
    "error": "Error al exportar a Excel: Se requiere openpyxl o xlsxwriter para exportar a Excel. Instale con: pip install openpyxl"
}
```
**Solución:** Instala las dependencias necesarias en el servidor:
```bash
pip install openpyxl  # Para Excel
pip install reportlab  # Para PDF
```

---

## 🔗 Enlaces Relacionados

- [Documentación de Arquitectura](arquitectura-sistema.md)
- [Especificaciones Técnicas](especificaciones-tecnicas.md)
- [Matriz de Dependencias](matriz-dependencias.md)

---

*Última actualización: Enero 2024*
### Login (/api/core/auth/login/)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

### Refresh Token (/api/core/auth/refresh/)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

### Logout (/api/core/auth/logout/)
Request body:
```json
{
  "refresh_token": "<tu_refresh_token>"
}
```
Response:
```json
{
  "message": "Sesión cerrada exitosamente"
}
```