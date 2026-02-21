# 🏗️ Arquitectura del Sistema - Arte Ideas

## Resumen Ejecutivo de la Arquitectura

El backend de **Arte Ideas** está diseñado como un sistema **multi-tenant** con **6 aplicaciones Django** que agrupan los 12 módulos frontend por dominio de negocio, priorizando la cohesión funcional y el bajo acoplamiento.

### 📦 Aplicaciones Backend Propuestas

| App Backend | Módulos Frontend | Responsabilidad Principal |
|-------------|------------------|---------------------------|
| **Core** | Mi Perfil, Configuración | Autenticación, usuarios, configuración sistema |
| **CRM** | Clientes, Agenda, Contratos | Gestión de relaciones con clientes |
| **Commerce** | Pedidos, Inventario | Operaciones comerciales y stock |
| **Operations** | Producción, Activos | Operaciones internas y recursos |
| **Finance** | Gastos | Gestión financiera y contable |
| **Analytics** | Dashboard, Reportes | Métricas, análisis y reportería |

## 🎯 Principios de Diseño Aplicados

### 1. Agrupación por Dominio de Negocio
- ❌ **NO**: 12 apps (1:1 con frontend)
- ✅ **SÍ**: 6 apps cohesivas por dominio

### 2. Bajo Acoplamiento
- Cada app puede funcionar independientemente
- Dependencias mínimas y bien definidas
- Interfaces claras entre apps

### 3. Alta Cohesión
- Funcionalidades relacionadas agrupadas
- Modelos con responsabilidades claras
- Lógica de negocio centralizada por dominio

## 🔗 Mapa de Relaciones

```
Core (Base)
├── Usuarios, Roles, Configuración
└── Requerido por: TODAS las apps

CRM (Independiente)
├── Clientes, Agenda, Contratos
└── Dependencias: Core

Commerce (Nivel 1)
├── Pedidos, Inventario
└── Dependencias: Core, CRM

Operations (Nivel 1)
├── Producción, Activos
└── Dependencias: Core, Commerce

Finance (Nivel 2)
├── Gastos
└── Dependencias: Core, Commerce, Operations

Analytics (Nivel 2)
├── Dashboard, Reportes
└── Dependencias: TODAS (para métricas)
```

## 🏛️ Arquitectura Multi-Tenant

### Estrategia: Shared Database + Tenant Isolation
- **Una base de datos** para todos los tenants
- **Aislamiento por `tenant_id`** en cada modelo
- **Filtros automáticos** en querysets
- **Middleware** para contexto de tenant

### Ventajas de esta Arquitectura
- ✅ Escalabilidad horizontal
- ✅ Mantenimiento simplificado
- ✅ Costos optimizados
- ✅ Backup y migración centralizados

## 🛡️ Sistema de Seguridad

### Roles Base (según frontend React)
1. **admin (Administrador)**: Acceso completo al sistema, gestión de usuarios y configuración
2. **manager (Gerente)**: Gestión operativa, reportes y supervisión general  
3. **employee (Empleado)**: Operaciones diarias, gestión de pedidos y clientes
4. **photographer (Fotógrafo)**: Especializado en desarrollo de pedidos fotográficos y sesiones
5. **assistant (Asistente)**: Soporte administrativo y tareas básicas

### Permisos Granulares
- Control a nivel de **módulo**
- Control a nivel de **acción** (CRUD)
- **Permisos custom** por tenant
- **Herencia de roles** configurable

## 📊 Justificación de Agrupaciones

### ¿Por qué Core?
- **Usuarios y autenticación** son transversales
- **Configuración** afecta todo el sistema
- **Base común** para multi-tenancy

### ¿Por qué CRM?
- **Clientes** son el centro de agenda y contratos
- **Flujo natural**: Cliente → Cita → Contrato
- **Dominio cohesivo** de relaciones

### ¿Por qué Commerce?
- **Pedidos** requieren consulta de materiales disponibles
- **Registro de materiales** se actualiza manualmente
- **Ciclo comercial** completo

### ¿Por qué Operations?
- **Desarrollo de pedidos** utiliza equipos y activos del estudio para elaborar marcos, impresiones, etc.
- **Activos** (cámaras, impresoras, equipos) requieren mantenimiento y control
- **Operaciones internas** del estudio fotográfico relacionadas

### ¿Por qué Finance separado?
- **Gastos** pueden existir sin pedidos
- **Contabilidad** tiene reglas específicas
- **Reportes financieros** especializados

### ¿Por qué Analytics separado?
- **Dashboard** consume datos de todas las apps
- **Reportes** requieren agregaciones complejas
- **Métricas** transversales al negocio

## 🔄 Flujo de Datos Típico

```
1. Usuario (Core) → 
2. Cliente (CRM) → 
3. Pedido (Commerce) → 
4. Desarrollo de pedido (Operations) → 
5. Gasto (Finance) → 
6. Reporte (Analytics)
```

## 📈 Escalabilidad Futura

### Horizontal
- Nuevos módulos se integran fácilmente
- Apps independientes permiten equipos separados
- Microservicios futuros por app

### Vertical
- Optimización por app específica
- Cache independiente por dominio
- Base de datos particionada por tenant

---
*Arquitectura diseñada para escalabilidad, mantenibilidad y desarrollo ágil*