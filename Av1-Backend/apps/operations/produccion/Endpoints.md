# 🏭 Arte Ideas - Producción API

Sistema de gestión de órdenes de producción para estudios fotográficos con arquitectura multi-tenant.

## 📋 Tabla de Contenidos

- [🎯 Descripción](#-descripción)
- [🔌 Endpoints Disponibles](#-endpoints-disponibles)
- [🧪 Testing con Postman](#-testing-con-postman)
- [📊 Modelos de Datos](#-modelos-de-datos)
- [🔐 Autenticación](#-autenticación)
- [🏢 Multi-Tenancy](#️-multi-tenancy)
- [📝 Ejemplos de Uso](#-ejemplos-de-uso)

---

## 🎯 Descripción

La **API de Producción** permite gestionar órdenes de producción fotográfica con funcionalidades completas de CRUD, filtrado avanzado y estadísticas. Está integrada con los modelos reales del sistema:

- ✅ **Órdenes de Producción** con estados y prioridades
- ✅ **Integración con Pedidos** (Commerce)
- ✅ **Gestión de Clientes** (CRM)
- ✅ **Asignación de Operarios** (Core Users)
- ✅ **Aislamiento por Tenant** (Multi-tenancy)

---

## 🔌 Endpoints Disponibles

### 📋 Base URL
```
http://localhost:8000/api/operations/produccion/ordenes/
```

### 🎯 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Listar todas las órdenes de producción |
| `POST` | `/` | Crear nueva orden de producción |
| `GET` | `/{id}/` | Obtener detalles de una orden específica |
| `PUT` | `/{id}/` | Actualizar orden completa |
| `PATCH` | `/{id}/` | Actualizar orden parcialmente |
| `DELETE` | `/{id}/` | Eliminar orden |
| `GET` | `/dashboard/` | Obtener estadísticas del dashboard |

---

## 🧪 Testing con Postman

### 🔐 Configuración Inicial

#### 1. Variables de Entorno
Crear un environment en Postman con las siguientes variables:

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "{{token_obtenido_del_login}}",
  "tenant_id": "1"
}
```

#### 2. Headers Requeridos
Todos los endpoints requieren autenticación JWT:

```http
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

### 📝 Colección de Endpoints

#### 🔑 1. Autenticación (Prerequisito)
```http
POST {{base_url}}/api/core/auth/login/
Content-Type: application/json

{
  "username": "admin_usuario",
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin_usuario",
    "role": "admin",
    "tenant": 1
  }
}
```

#### 📋 2. Listar Órdenes de Producción
```http
GET {{base_url}}/api/operations/produccion/ordenes/
Authorization: Bearer {{access_token}}
```

**Parámetros de Query Opcionales:**
- `search`: Búsqueda general
- `estado`: Filtrar por estado
- `tipo`: Filtrar por tipo
- `prioridad`: Filtrar por prioridad
- `cliente`: Filtrar por cliente
- `fecha_estimada__gte`: Fecha desde
- `fecha_estimada__lte`: Fecha hasta

**Ejemplo con filtros:**
```http
GET {{base_url}}/api/operations/produccion/ordenes/?estado=Pendiente&tipo=Enmarcado
```

**Respuesta:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/operations/produccion/ordenes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero_op": "OP-001",
      "pedido": 1,
      "pedido_codigo": "ORD-001",
      "cliente": 1,
      "cliente_nombre": "Juan Pérez",
      "descripcion": "Enmarcado de fotos familiares",
      "tipo": "Enmarcado",
      "estado": "Pendiente",
      "prioridad": "Normal",
      "operario": 2,
      "operario_nombre": "María García",
      "fecha_estimada": "2024-01-15",
      "creado_en": "2024-01-10T10:00:00Z",
      "actualizado_en": "2024-01-10T10:00:00Z"
    }
  ]
}
```

#### ➕ 3. Crear Nueva Orden de Producción
```http
POST {{base_url}}/api/operations/produccion/ordenes/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "numero_op": "OP-002",
  "pedido": 1,
  "descripcion": "Impresión de fotos de graduación",
  "tipo": "Minilab",
  "estado": "Pendiente",
  "prioridad": "Alta",
  "operario": 2,
  "fecha_estimada": "2024-01-20"
}
```

**Respuesta:**
```json
{
  "id": 2,
  "numero_op": "OP-002",
  "pedido": 1,
  "pedido_codigo": "ORD-001",
  "cliente": 1,
  "cliente_nombre": "Juan Pérez",
  "descripcion": "Impresión de fotos de graduación",
  "tipo": "Minilab",
  "estado": "Pendiente",
  "prioridad": "Alta",
  "operario": 2,
  "operario_nombre": "María García",
  "fecha_estimada": "2024-01-20",
  "creado_en": "2024-01-10T11:00:00Z",
  "actualizado_en": "2024-01-10T11:00:00Z"
}
```

#### 👁️ 4. Obtener Detalles de Orden
```http
GET {{base_url}}/api/operations/produccion/ordenes/1/
Authorization: Bearer {{access_token}}
```

#### ✏️ 5. Actualizar Orden (Completa)
```http
PUT {{base_url}}/api/operations/produccion/ordenes/1/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "numero_op": "OP-001",
  "pedido": 1,
  "descripcion": "Enmarcado de fotos familiares - ACTUALIZADO",
  "tipo": "Enmarcado",
  "estado": "En Proceso",
  "prioridad": "Alta",
  "operario": 2,
  "fecha_estimada": "2024-01-18"
}
```

#### 🔧 6. Actualizar Orden (Parcial)
```http
PATCH {{base_url}}/api/operations/produccion/ordenes/1/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "estado": "Terminado",
  "prioridad": "Normal"
}
```

#### 🗑️ 7. Eliminar Orden
```http
DELETE {{base_url}}/api/operations/produccion/ordenes/1/
Authorization: Bearer {{access_token}}
```

#### 📊 8. Dashboard de Estadísticas
```http
GET {{base_url}}/api/operations/produccion/ordenes/dashboard/
Authorization: Bearer {{access_token}}
```

**Respuesta:**
```json
{
  "pendientes": 5,
  "en_proceso": 3,
  "terminados": 8,
  "entregados": 12,
  "total": 28
}
```

**Para Superusuarios (con parámetro de tenant):**
```http
GET {{base_url}}/api/operations/produccion/ordenes/dashboard/?inquilino_id=1
```

---

## 📊 Modelos de Datos

### 🏭 OrdenProduccion

```python
{
  "id": "integer (auto)",
  "numero_op": "string (max 20, unique)",
  "pedido": "integer (FK to Order)",
  "cliente": "integer (FK to Client, auto-filled)",
  "descripcion": "text",
  "tipo": "choice ['Enmarcado', 'Minilab', 'Graduación', 'Corte Láser', 'Edición Digital', 'Otro']",
  "estado": "choice ['Pendiente', 'En Proceso', 'Terminado', 'Entregado']",
  "prioridad": "choice ['Baja', 'Normal', 'Media', 'Alta']",
  "operario": "integer (FK to User with role='operario')",
  "fecha_estimada": "date",
  "id_inquilino": "integer (FK to Tenant, auto-assigned)",
  "creado_en": "datetime (auto)",
  "actualizado_en": "datetime (auto)"
}
```

### 🔍 Filtros Disponibles

| Campo | Operadores | Ejemplo |
|-------|------------|---------|
| `estado` | `exact` | `?estado=Pendiente` |
| `tipo` | `exact` | `?tipo=Enmarcado` |
| `prioridad` | `exact` | `?prioridad=Alta` |
| `cliente` | `exact` | `?cliente=1` |
| `fecha_estimada` | `gte`, `lte` | `?fecha_estimada__gte=2024-01-15` |
| `search` | `icontains` | `?search=OP-001` |

### 🔍 Campos de Búsqueda General
La búsqueda general (`search`) busca en:
- `numero_op`
- `pedido__order_number`
- `cliente__first_name`
- `cliente__last_name`
- `descripcion`

---

## 🔐 Autenticación

### 🎫 JWT Token
Todos los endpoints requieren un token JWT válido:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 👤 Roles y Permisos
- **Superusuarios**: Acceso a todas las órdenes de todos los tenants
- **Usuarios normales**: Solo órdenes de su tenant
- **Operarios**: Filtrados por `role='operario'` en asignaciones

---

## 🏢 Multi-Tenancy

### 🔒 Aislamiento de Datos
- Cada usuario solo ve órdenes de su tenant
- El `id_inquilino` se asigna automáticamente
- Los superusuarios pueden ver todos los tenants

### 🎯 Filtrado Automático
```python
# Usuarios normales
OrdenProduccion.objects.filter(id_inquilino=user.tenant)

# Superusuarios
OrdenProduccion.objects.all()
```

---

## 📝 Ejemplos de Uso

### 🎯 Caso de Uso 1: Crear Orden para Enmarcado
```http
POST {{base_url}}/api/operations/produccion/ordenes/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "numero_op": "OP-ENM-001",
  "pedido": 5,
  "descripcion": "Enmarcado de 10 fotos 20x30cm con marco dorado",
  "tipo": "Enmarcado",
  "estado": "Pendiente",
  "prioridad": "Normal",
  "operario": 3,
  "fecha_estimada": "2024-01-25"
}
```

### 🎯 Caso de Uso 2: Buscar Órdenes Atrasadas
```http
GET {{base_url}}/api/operations/produccion/ordenes/?fecha_estimada__lt=2024-01-10&estado=Pendiente
Authorization: Bearer {{access_token}}
```

### 🎯 Caso de Uso 3: Actualizar Estado a "En Proceso"
```http
PATCH {{base_url}}/api/operations/produccion/ordenes/5/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "estado": "En Proceso"
}
```

### 🎯 Caso de Uso 4: Obtener Estadísticas del Dashboard
```http
GET {{base_url}}/api/operations/produccion/ordenes/dashboard/
Authorization: Bearer {{access_token}}
```

---

## ⚠️ Validaciones y Errores

### 🚫 Errores Comunes

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 400 Bad Request - Número de OP duplicado
```json
{
  "numero_op": ["Este número de orden ya existe."]
}
```

#### 400 Bad Request - Operario inválido
```json
{
  "operario": ["El usuario seleccionado no tiene el rol de Operario."]
}
```

#### 403 Forbidden - Sin permisos
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### ✅ Validaciones Automáticas
- **Cliente**: Se autocompleta desde el pedido seleccionado
- **Tenant**: Se asigna automáticamente del usuario autenticado
- **Operario**: Debe tener `role='operario'`
- **Número OP**: Debe ser único por tenant

---

## 🔧 Configuración de Postman

### 📁 Pre-request Script para Autenticación
```javascript
// Pre-request script para mantener token actualizado
if (!pm.environment.get("access_token")) {
    pm.sendRequest({
        url: pm.environment.get("base_url") + "/api/core/auth/login/",
        method: 'POST',
        header: {
            'Content-Type': 'application/json',
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                username: pm.environment.get("username"),
                password: pm.environment.get("password")
            })
        }
    }, function (err, response) {
        if (response.code === 200) {
            const jsonData = response.json();
            pm.environment.set("access_token", jsonData.access);
        }
    });
}
```

### 🧪 Tests Automáticos
```javascript
// Test para verificar respuesta exitosa
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('numero_op');
    pm.expect(jsonData).to.have.property('estado');
});

// Guardar ID para siguientes requests
if (pm.response.code === 201) {
    const jsonData = pm.response.json();
    pm.environment.set("orden_id", jsonData.id);
}
```

---

## 📚 Documentación Adicional

### 🔗 Enlaces Relacionados
- **API Base**: `http://localhost:8000/api/operations/`
- **Django Admin**: `http://localhost:8000/admin/`
- **Health Check**: `http://localhost:8000/api/core/health/`

### 📋 Dependencias
- **Commerce App**: Para modelos de `Order`
- **CRM App**: Para modelos de `Client`
- **Core App**: Para modelos de `User` y `Tenant`

---

**🎨 Arte Ideas - Producción API v1.0**  
*Sistema de gestión de órdenes de producción fotográfica*