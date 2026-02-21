# Endpoints del Proyecto (Arte Ideas Backend)

- Base URL: `http://localhost:8000`
- Autenticación: JWT Bearer (`Authorization: Bearer <token>`)
- Content-Type: `application/json`

## Autenticación (Core)
- `POST /api/core/auth/login/` — Obtención de tokens (access y refresh)
  - Ejemplo:
    ```bash
    curl -X POST http://localhost:8000/api/core/auth/login/ \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"tu_password"}'
    ```
- `POST /api/core/auth/refresh/` — Renovar token de acceso
  - Ejemplo:
    ```bash
    curl -X POST http://localhost:8000/api/core/auth/refresh/ \
      -H "Content-Type: application/json" \
      -d '{"refresh":"<refresh_token>"}'
    ```
- `POST /api/core/auth/logout/` — Invalidar refresh token
  - Ejemplo:
    ```bash
    curl -X POST http://localhost:8000/api/core/auth/logout/ \
      -H "Authorization: Bearer <access_token>" \
      -H "Content-Type: application/json" \
      -d '{"refresh_token":"<refresh_token>"}'
    ```

## Core
- Salud del sistema
  - `GET /api/core/health/`
    - Ejemplo:
      ```bash
      curl -X GET http://localhost:8000/api/core/health/ -H "Authorization: Bearer <token>"
      ```
- Usuarios (`apps/core/usuarios/views.py`)
  - `GET /api/core/users/profile/` — Perfil actual
  - `PUT /api/core/users/profile/` — Actualizar perfil
    - Ejemplo:
      ```bash
      curl -X PUT http://localhost:8000/api/core/users/profile/ \
        -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
        -d '{"first_name":"Edu","last_name":"Pérez","phone":"999999999"}'
      ```
  - `GET /api/core/users/profile/statistics/`
  - `GET /api/core/users/profile/completion/`
  - `GET /api/core/users/profile/activity/`
  - `POST /api/core/users/change-password/`
    - Ejemplo:
      ```bash
      curl -X POST http://localhost:8000/api/core/users/change-password/ \
        -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
        -d '{"current_password":"anterior","new_password":"NuevaSegura123"}'
      ```
  - `POST /api/core/users/change-email/`
    - Ejemplo:
      ```bash
      curl -X POST http://localhost:8000/api/core/users/change-email/ \
        -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
        -d '{"new_email":"nuevo@correo.com"}'
      ```
- Configuración del sistema (`apps/core/configuracion_sistema/urls.py`)
  - `GET /api/core/config/business/`
  - `GET /api/core/config/users/`
  - `GET /api/core/config/users/{user_id}/`
  - `GET /api/core/config/roles/`
  - `GET /api/core/config/permissions/`
  - `GET /api/core/config/permissions/{role}/`
  - `GET /api/core/config/tenants/`
  - `GET /api/core/config/tenants/{tenant_id}/users/`

## CRM
- Clientes (`apps/crm/clientes/urls.py`)
  - Router DRF bajo `/api/crm/clientes/`:
    - `GET /api/crm/clientes/clientes/` — Listar
    - `POST /api/crm/clientes/clientes/` — Crear
      - Ejemplo crear cliente:
        ```bash
        curl -X POST http://localhost:8000/api/crm/clientes/clientes/ \
          -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
          -d '{
                "tipo_cliente":"particular",
                "nombres":"Juan",
                "apellidos":"García",
                "email":"juan@ejemplo.com",
                "telefono":"987654321",
                "dni":"12345678",
                "direccion":"Av. Siempre Viva 123"
              }'
        ```
    - `GET /api/crm/clientes/clientes/{id}/`
    - `PUT /api/crm/clientes/clientes/{id}/`
    - `PATCH /api/crm/clientes/clientes/{id}/`
    - `DELETE /api/crm/clientes/clientes/{id}/`
    - `GET|POST|PUT|PATCH|DELETE /api/crm/clientes/contactos/…` — Contactos
    - `GET|POST|PUT|PATCH|DELETE /api/crm/clientes/historial/…` — Historial
- Agenda (`apps/crm/agenda/urls.py`)
  - Router DRF bajo `/api/crm/agenda/`:
    - `GET|POST /api/crm/agenda/eventos/` ; `GET|PUT|PATCH|DELETE /api/crm/agenda/eventos/{id}/`
    - `GET|POST /api/crm/agenda/citas/` ; `GET|PUT|PATCH|DELETE /api/crm/agenda/citas/{id}/`
    - `GET|POST /api/crm/agenda/recordatorios/` ; `GET|PUT|PATCH|DELETE /api/crm/agenda/recordatorios/{id}/`
  - Vistas adicionales:
    - `GET /api/crm/agenda/dashboard/`
    - `GET /api/crm/agenda/proximos-eventos/`
    - `GET /api/crm/agenda/proximos-eventos-demo/`
    - `GET /api/crm/agenda/eventos-hoy/`
    - `GET /api/crm/agenda/citas-pendientes/`
- Contratos (`apps/crm/contratos/urls.py`)
  - Router DRF bajo `/api/crm/contratos/`:
    - `GET|POST /api/crm/contratos/contratos/` ; `GET|PUT|PATCH|DELETE /api/crm/contratos/contratos/{id}/`
    - `GET|POST /api/crm/contratos/clausulas/` ; `GET|PUT|PATCH|DELETE /api/crm/contratos/clausulas/{id}/`
    - `GET|POST /api/crm/contratos/pagos/` ; `GET|PUT|PATCH|DELETE /api/crm/contratos/pagos/{id}/`
    - `GET|POST /api/crm/contratos/estados/` ; `GET|PUT|PATCH|DELETE /api/crm/contratos/estados/{id}/`

## Commerce
- Pedidos (`apps/commerce/pedidos/urls.py`)
  - Router DRF (compatibilidad) bajo `/api/commerce/pedidos/` y también bajo `/api/commerce/pedidos/api/`:
    - `GET|POST /api/commerce/pedidos/orders/` ; `GET|PUT|PATCH|DELETE /api/commerce/pedidos/orders/{id}/`
    - `GET|POST /api/commerce/pedidos/order-items/` ; `GET|PUT|PATCH|DELETE /api/commerce/pedidos/order-items/{id}/`
    - `GET|POST /api/commerce/pedidos/payments/` ; `GET|PUT|PATCH|DELETE /api/commerce/pedidos/payments/{id}/`
    - `GET|POST /api/commerce/pedidos/status-history/` ; `GET|PUT|PATCH|DELETE /api/commerce/pedidos/status-history/{id}/`
  - Acciones específicas (notar prefijo `/api/` del módulo):
    - `GET /api/commerce/pedidos/api/orders/estadisticas/`
    - `GET /api/commerce/pedidos/api/orders/resumen/`
    - `GET /api/commerce/pedidos/api/orders/atrasados/`
    - `GET /api/commerce/pedidos/api/orders/proximas-entregas/`
    - `GET /api/commerce/pedidos/api/orders/por-estado/?status=<estado>`
    - `POST /api/commerce/pedidos/api/orders/{id}/cambiar-estado/` — body `{ "status": "en_proceso", "reason": "Comentario" }`
    - `POST /api/commerce/pedidos/api/orders/{id}/marcar-completado/`
    - `POST /api/commerce/pedidos/api/orders/{id}/marcar-cancelado/` — body `{ "reason": "Motivo" }`
    - `GET /api/commerce/pedidos/api/orders/{id}/pagos/`
    - `POST /api/commerce/pedidos/api/orders/{id}/registrar-pago/` — body ver ejemplo abajo
    - `GET /api/commerce/pedidos/api/orders/{id}/historial-estados/`
  - Ejemplos:
    - Crear pedido mínimo:
      ```bash
      curl -X POST http://localhost:8000/api/commerce/pedidos/orders/ \
        -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
        -d '{
              "order_number":"OP-0001",
              "cliente": 1,
              "document_type":"proforma",
              "order_date":"2025-01-15",
              "delivery_date":"2025-01-30",
              "total": 250.00,
              "status":"pendiente"
            }'
      ```
    - Registrar pago en pedido `{id}`:
      ```bash
      curl -X POST http://localhost:8000/api/commerce/pedidos/api/orders/1/registrar-pago/ \
        -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
        -d '{
              "payment_date":"2025-01-16",
              "amount": 100.00,
              "payment_method":"efectivo",
              "reference_number":"REC-1001",
              "notes":"Pago en caja"
            }'
      ```
- Inventario (`apps/commerce/inventario/urls.py`)
  - Router DRF bajo `/api/commerce/inventario/` y también bajo `/api/commerce/inventario/api/`:
    - Enmarcados: `moldura-liston`, `moldura-prearmada`, `vidrio-tapa-mdf`, `paspartu`
    - Minilab: `minilab`
    - Graduaciones: `cuadros`, `anuarios`
    - Corte Láser: `corte-laser`
    - Accesorios: `marco-accesorio`, `herramienta-general`
    - Ejemplo listar molduras (listón):
      ```bash
      curl -X GET http://localhost:8000/api/commerce/inventario/moldura-liston/ \
        -H "Authorization: Bearer <token>"
      ```
  - Endpoints adicionales (prefijo `/api/` del módulo):
    - `GET /api/commerce/inventario/api/dashboard/`
    - `GET /api/commerce/inventario/api/metricas/`
    - Alertas de stock por categoría (GET):
      - `/api/commerce/inventario/api/moldura-liston/alertas-stock/`
      - `/api/commerce/inventario/api/moldura-prearmada/alertas-stock/`
      - `/api/commerce/inventario/api/vidrio-tapa-mdf/alertas-stock/`
      - `/api/commerce/inventario/api/paspartu/alertas-stock/`
      - `/api/commerce/inventario/api/minilab/alertas-stock/`
      - `/api/commerce/inventario/api/cuadros/alertas-stock/`
      - `/api/commerce/inventario/api/anuarios/alertas-stock/`
      - `/api/commerce/inventario/api/corte-laser/alertas-stock/`
      - `/api/commerce/inventario/api/marco-accesorio/alertas-stock/`
      - `/api/commerce/inventario/api/herramienta-general/alertas-stock/`

## Operations
- Producción (`apps/operations/produccion/urls.py`)
  - Router DRF bajo `/api/operations/produccion/` y también bajo `/api/operations/produccion/api/`:
    - `GET|POST /api/operations/produccion/ordenes/` ; `GET|PUT|PATCH|DELETE /api/operations/produccion/ordenes/{id}/`
    - Crear orden de producción:
      ```bash
      curl -X POST http://localhost:8000/api/operations/produccion/ordenes/ \
        -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
        -d '{
              "numero_op":"OP-2025-001",
              "pedido": 10,
              "descripcion":"Impresión y enmarcado",
              "tipo":"enmarcado",
              "estado":"pendiente",
              "prioridad":"alta",
              "operario": 3,
              "fecha_estimada":"2025-01-25"
            }'
      ```
  - Acciones específicas (prefijo `/api/` del módulo):
    - `GET /api/operations/produccion/api/ordenes/dashboard/`
    - `GET /api/operations/produccion/api/ordenes/por-estado/?estado=<estado>`
    - `GET /api/operations/produccion/api/ordenes/por-tipo/?tipo=<tipo>`
    - `GET /api/operations/produccion/api/ordenes/por-operario/?operario_id=<id>`
    - `GET /api/operations/produccion/api/ordenes/vencidas/`
    - `GET /api/operations/produccion/api/ordenes/proximas/`
    - `GET /api/operations/produccion/api/ordenes/resumen-produccion/`
    - `POST /api/operations/produccion/api/ordenes/{id}/cambiar-estado/` — body `{ "estado": "en_proceso" }`
    - `POST /api/operations/produccion/api/ordenes/{id}/marcar-completado/`
- Activos (`apps/operations/activos/urls.py`)
  - Router DRF bajo `/api/operations/activos/` y también bajo `/api/operations/activos/api/`:
    - `GET|POST /api/operations/activos/activos/` ; `GET|PUT|PATCH|DELETE /api/operations/activos/activos/{id}/`
    - `GET|POST /api/operations/activos/financiamientos/` ; `GET|PUT|PATCH|DELETE /api/operations/activos/financiamientos/{id}/`
    - `GET|POST /api/operations/activos/mantenimientos/` ; `GET|PUT|PATCH|DELETE /api/operations/activos/mantenimientos/{id}/`
    - `GET|POST /api/operations/activos/repuestos/` ; `GET|PUT|PATCH|DELETE /api/operations/activos/repuestos/{id}/`
  - Endpoints adicionales:
    - `GET /api/operations/activos/api/dashboard/`
    - `GET /api/operations/activos/api/activos/por-categoria/?categoria=<code>`
    - `GET /api/operations/activos/api/activos/depreciacion-report/`
    - `GET /api/operations/activos/api/activos/mantenimientos-pendientes/`
    - `GET /api/operations/activos/api/mantenimientos/proximos/?dias=30`
    - `GET /api/operations/activos/api/mantenimientos/vencidos/`
    - `POST /api/operations/activos/api/mantenimientos/{id}/completar/` — body `{ "proxima_fecha_mantenimiento":"2025-02-15", "estado_del_activo":"activo" }`
    - `GET /api/operations/activos/api/repuestos/alertas-stock/`
    - `GET /api/operations/activos/api/repuestos/sin-stock/`
    - `POST /api/operations/activos/api/repuestos/{id}/actualizar-stock/` — body `{ "operacion":"agregar", "cantidad":5, "motivo":"Ajuste" }`
    - `GET /api/operations/activos/api/repuestos/resumen-inventario/`
    - `GET /api/operations/activos/api/financiamientos/resumen-financiero/`
    - `POST /api/operations/activos/api/financiamientos/{id}/marcar-pagado/`

## Analytics
- Dashboard (`apps/analytics/dashboard/urls.py`)
  - `GET /api/analytics/dashboard/resumen/`
  - `GET /api/analytics/dashboard/alertas/`
  - `GET /api/analytics/dashboard/alertas-rapidas/`
  - `GET /api/analytics/dashboard/estado-produccion/`
  - `GET /api/analytics/dashboard/clientes-estadisticas/`
  - `GET /api/analytics/dashboard/contratos-estadisticas/`
  - `GET /api/analytics/dashboard/productos-mas-vendidos/`
  - `GET /api/analytics/dashboard/pedidos-recientes/`
  - `GET /api/analytics/dashboard/entregas-programadas-hoy/`
- Reportes (`apps/analytics/Reportes/urls.py`)
  - `GET /api/analytics/reportes/categorias/`
  - `GET /api/analytics/reportes/todos/`
  - `GET /api/analytics/reportes/{categoria}/`
  - `GET /api/analytics/reportes/{categoria}/exportar/excel/`
  - `GET /api/analytics/reportes/{categoria}/exportar/pdf/`

## Admin Django
- `GET /admin/` — Panel de administración

## Notas
- La mayoría de endpoints requieren `Authorization: Bearer <token>` (excepto login y refresh).
- Los routers DRF generan automáticamente endpoints CRUD estándar: `GET` (lista/detalle), `POST` (crear), `PUT/PATCH` (actualizar), `DELETE` (eliminar).
- En algunos módulos hay compatibilidad de rutas bajo el mismo prefijo con y sin `api/`; para acciones específicas usa la variante con `api/` indicada arriba.
