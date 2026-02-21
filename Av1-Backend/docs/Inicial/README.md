# Documentación Backend - Arte Ideas

Sistema multi-tenant de gestión para estudios fotográficos desarrollado con Django REST Framework.

## 📁 Estructura de Documentación

- [Arquitectura del Sistema](./arquitectura-sistema.md) - Diseño general y principios
- [Aplicaciones Backend](./aplicaciones-backend.md) - Apps Django y responsabilidades
- [Matriz de Dependencias](./matriz-dependencias.md) - Relaciones entre apps
- [Plan de Desarrollo Sprint](./plan-desarrollo-sprint.md) - Backlog de 7 días
- [Sistema Multi-Tenancy](./sistema-multi-tenancy.md) - Implementación de tenants
- [Sistema de Exportación](./sistema-exportacion.md) - Funcionalidades de export
- [Especificaciones Técnicas](./especificaciones-tecnicas.md) - Stack y requerimientos
- [Compatibilidad Frontend](./compatibilidad-frontend.md) - Integración con React frontend

## 🎯 Resumen Ejecutivo

**Arte Ideas** es un sistema de gestión especializado para estudios fotográficos que agrupa los 12 módulos frontend en **6 aplicaciones Django** optimizadas por dominio de negocio fotográfico:

1. **Core** (Autenticación, Perfiles, Configuración del sistema)
2. **CRM** (Clientes, Agenda fotográfica, Contratos de servicios)
3. **Commerce** (Pedidos fotográficos, Registro de materiales)
4. **Operations** (Desarrollo de pedidos, Activos y equipos)
5. **Finance** (Gastos operativos, Control financiero)
6. **Analytics** (Dashboard ejecutivo, Reportes de negocio)

### 🏗️ Principios Arquitectónicos
- ✅ Apps desacopladas con responsabilidades claras
- ✅ Multi-tenancy transparente con tenant_id
- ✅ Sistema de roles granular (5 roles específicos: admin, manager, employee, photographer, assistant)
- ✅ Exportación modular (PDF, Excel, CSV)
- ✅ Orden de desarrollo basado en dependencias

### ⏱️ Timeline de Desarrollo
- **Días 1-2**: Core + CRM (base independiente, compatible con React frontend)
- **Días 3-4**: Commerce + Operations (dependencias nivel 1)
- **Días 5-6**: Finance + Analytics (dependencias nivel 2)
- **Día 7**: Integración, testing y compatibilidad frontend

### 🔗 Compatibilidad Frontend
Esta documentación está **100% basada en el análisis del código React frontend existente**, garantizando:
- ✅ APIs compatibles con servicios existentes (api.js, clientesService.js, etc.)
- ✅ Modelos de datos con campos exactos esperados por el frontend
- ✅ Respuestas JSON en formato específico del frontend
- ✅ Sistema de autenticación compatible con authService.js
- ✅ Endpoints con estructura esperada por el frontend React

---
*Documentación generada específicamente para el frontend React existente de Arte Ideas*