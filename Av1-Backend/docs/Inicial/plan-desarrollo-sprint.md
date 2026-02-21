# 🚀 Plan de Desarrollo Sprint (7 días) - Arte Ideas

## 📅 Distribución Semanal

| Día | Apps | Prioridad | Horas Est. | Estado |
|-----|------|-----------|------------|--------|
| **1** | Core (Setup + Base) | 🔴 CRÍTICA | 8h | Bloqueante |
| **2** | CRM + Finance (Gastos) | 🟡 ALTA | 8h | Paralelo |
| **3** | Commerce | 🟡 ALTA | 8h | Secuencial |
| **4** | Operations | 🟠 MEDIA | 8h | Secuencial |
| **5** | Finance (Pagos) + Analytics (Base) | 🟠 MEDIA | 8h | Paralelo |
| **6** | Analytics (Reportes) + Integraciones | 🟢 BAJA | 8h | Final |
| **7** | Testing + Documentación | 🟢 BAJA | 8h | Cierre |

---

## 📋 DÍA 1 - CORE APP (Base del Sistema)

### 📋 TÍTULO: [Core] - Setup Inicial + Autenticación + Multi-tenancy

**📝 DESCRIPCIÓN:**
- Objetivo: Establecer la base del sistema multi-tenant con autenticación JWT compatible con React frontend
- Modelos: Tenant, User, Role, SystemConfiguration
- Endpoints: Auth (formato específico para authService.js), Profile, Configuration, Roles
- Lógica de negocio: Multi-tenancy, permisos, configuración, flujo cambio contraseña
- Permisos: Todos los roles (base del sistema)
- Compatibilidad: Respuestas JSON exactas para el frontend React

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `core/models.py`: Tenant, User (roles específicos del frontend), Role, SystemConfiguration
   - `core/serializers.py`: UserSerializer (campos compatibles), TenantSerializer, RoleSerializer, ConfigSerializer
   - `core/views.py`: AuthLoginView (respuesta específica), ProfileViewSet, ConfigurationViewSet, RoleViewSet
   - `core/urls.py`: /auth/login/, /auth/logout/, /auth/profile/, /configuration/, /roles/
   - `core/permissions.py`: TenantPermission, RolePermission, IsOwnerOrAdmin
   - `core/middleware.py`: TenantMiddleware + FrontendCompatibilityMiddleware
   - `core/services.py`: TenantService, AuthService (compatible con authService.js)

2. **Funcionalidades implementadas:**
   - Autenticación JWT con formato específico del frontend
   - Flujo completo de cambio de contraseña (requiresPasswordChange)
   - Registro automático de tenant en contexto
   - CRUD de usuarios con roles específicos (admin, employee, etc.)
   - Configuración por tenant
   - Sistema de permisos compatible con frontend
   - CORS configurado para Vite dev server (localhost:5173)

3. **Tests mínimos:**
   - Test de autenticación JWT
   - Test de aislamiento por tenant
   - Test de permisos básicos

4. **Dependencias resueltas:**
   - Ninguna (app base)

**⏱️ ESTIMACIÓN:** 8 horas  
**🏷️ PRIORIDAD:** 🔴 CRÍTICA

---

## 📋 DÍA 2 - CRM + FINANCE (Gastos)

### 📋 TÍTULO: [CRM] - Clientes + Agenda + Contratos

**📝 DESCRIPCIÓN:**
- Objetivo: Sistema completo de gestión de clientes del estudio fotográfico y relaciones
- Modelos: Client (con campos específicos: nombre, tipo, contacto, ie, direccion, detalles, documento), Appointment, Contract
- Endpoints: CRUD clientes, agenda fotográfica, contratos de servicios con PDF
- Lógica de negocio: Validaciones de citas fotográficas, generación contratos de promociones escolares
- Permisos: admin, manager (lectura/escritura), employee, photographer (gestión), assistant (solo lectura)

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `crm/models.py`: Client, Appointment, Contract con validaciones
   - `crm/serializers.py`: ClientSerializer, AppointmentSerializer, ContractSerializer
   - `crm/views.py`: ClientViewSet, AppointmentViewSet, ContractViewSet
   - `crm/urls.py`: /clients/, /appointments/, /contracts/
   - `crm/permissions.py`: CRMPermission, ClientOwnerPermission
   - `crm/services.py`: ContractPDFService, AppointmentService

2. **Funcionalidades implementadas:**
   - CRUD completo de clientes con búsqueda
   - Vista calendario para citas
   - Generación PDF de contratos
   - Validación de conflictos de horarios

3. **Tests mínimos:**
   - Test CRUD clientes
   - Test validación citas
   - Test generación PDF contratos

4. **Dependencias resueltas:**
   - Core completamente funcional

**⏱️ ESTIMACIÓN:** 5 horas  
**🏷️ PRIORIDAD:** 🟡 ALTA

### 📋 TÍTULO: [Finance] - Gastos + Categorías + Presupuestos

**📝 DESCRIPCIÓN:**
- Objetivo: Gestión de gastos operativos del estudio fotográfico
- Modelos: PersonalExpense (nómina: código, nombre, cargo, salarioBase, bonificaciones), ServiceExpense (servicios: tipo, proveedor, monto, fechaVenc, periodo)
- Endpoints: CRUD gastos de personal, gastos de servicios, control presupuestario
- Lógica de negocio: Flujo de pago de nómina, control de servicios (alquiler, luz, agua, internet), alertas vencimientos
- Permisos: admin (todo), manager (aprobación), employee (consulta), photographer, assistant (solo lectura)

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `finance/models.py`: Expense, ExpenseCategory, Budget
   - `finance/serializers.py`: ExpenseSerializer, CategorySerializer, BudgetSerializer
   - `finance/views.py`: ExpenseViewSet, CategoryViewSet, BudgetViewSet
   - `finance/urls.py`: /expenses/, /categories/, /budgets/
   - `finance/permissions.py`: ExpensePermission, BudgetPermission
   - `finance/services.py`: ExpenseApprovalService, BudgetControlService

2. **Funcionalidades implementadas:**
   - CRUD gastos con categorización
   - Sistema de aprobación de gastos
   - Control de presupuestos por categoría
   - Upload de comprobantes

3. **Tests mínimos:**
   - Test CRUD gastos
   - Test flujo aprobación
   - Test control presupuesto

4. **Dependencias resueltas:**
   - Core completamente funcional

**⏱️ ESTIMACIÓN:** 3 horas  
**🏷️ PRIORIDAD:** 🟠 MEDIA

---

## 📋 DÍA 3 - COMMERCE APP

### 📋 TÍTULO: [Commerce] - Registro de Materiales + Pedidos de Servicios

**📝 DESCRIPCIÓN:**
- Objetivo: Sistema completo de gestión de pedidos fotográficos y registro manual de materiales
- Modelos: Product (registro de materiales con categorías: enmarcados, minilab, graduaciones, corte láser), Order (con campos: cliente, servicio, cantidad, precio, adelanto), OrderItem, StockMovement
- Endpoints: CRUD materiales fotográficos, pedidos de servicios, registro manual de materiales, alertas stock
- Lógica de negocio: Registro manual de materiales fotográficos, validaciones pedidos de servicios, alertas de stock bajo
- Permisos: admin, manager (todo), employee, photographer (gestión pedidos), assistant (lectura limitada)

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `commerce/models.py`: Product, Order, OrderItem, StockMovement con signals
   - `commerce/serializers.py`: ProductSerializer, OrderSerializer, StockSerializer
   - `commerce/views.py`: ProductViewSet, OrderViewSet, InventoryViewSet
   - `commerce/urls.py`: /products/, /orders/, /inventory/
   - `commerce/permissions.py`: CommercePermission, OrderOwnerPermission
   - `commerce/services.py`: OrderService, InventoryService, StockAlertService
   - `commerce/signals.py`: Actualización automática de stock

2. **Funcionalidades implementadas:**
   - CRUD productos con categorías
   - Sistema completo de pedidos
   - Registro manual de materiales con alertas
   - Alertas de stock bajo
   - Confirmación y seguimiento de pedidos

3. **Tests mínimos:**
   - Test CRUD productos
   - Test creación pedidos
   - Test actualización stock automática
   - Test alertas stock bajo

4. **Dependencias resueltas:**
   - Core funcional
   - CRM.Client disponible para pedidos

**⏱️ ESTIMACIÓN:** 8 horas  
**🏷️ PRIORIDAD:** 🟡 ALTA

---

## 📋 DÍA 4 - OPERATIONS APP

### 📋 TÍTULO: [Operations] - Producción + Activos + Mantenimiento

**📝 DESCRIPCIÓN:**
- Objetivo: Gestión completa del desarrollo/elaboración de pedidos y activos del estudio
- Modelos: Asset (equipos fotográficos: cámaras, impresoras, maquinaria), ProductionOrder (órdenes fotográficas con campos: numeroOP, cliente, tipo, operario, fechaEstimada), ProductionTask, MaintenanceRecord
- Endpoints: CRUD activos fotográficos, órdenes de producción fotográfica, tareas de sesiones, mantenimiento equipos
- Lógica de negocio: Flujo de desarrollo de pedidos (elaboración de marcos, impresión, sesiones), programación mantenimiento equipos
- Permisos: admin, manager (todo), photographer (desarrollo de pedidos), employee (tareas), assistant (lectura)

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `operations/models.py`: Asset, ProductionOrder, ProductionTask, MaintenanceRecord
   - `operations/serializers.py`: AssetSerializer, ProductionSerializer, TaskSerializer, MaintenanceSerializer
   - `operations/views.py`: AssetViewSet, ProductionViewSet, TaskViewSet, MaintenanceViewSet
   - `operations/urls.py`: /assets/, /production/, /tasks/, /maintenance/
   - `operations/permissions.py`: OperationsPermission, ProductionPermission
   - `operations/services.py`: ProductionPlanningService, MaintenanceScheduleService

2. **Funcionalidades implementadas:**
   - CRUD activos con historial
   - Sistema de órdenes de desarrollo/elaboración
   - Gestión de tareas de desarrollo de pedidos
   - Programación de mantenimiento
   - Alertas de mantenimiento vencido

3. **Tests mínimos:**
   - Test CRUD activos
   - Test flujo desarrollo de pedidos
   - Test programación mantenimiento

4. **Dependencias resueltas:**
   - Core funcional
   - Commerce.Order disponible para órdenes de desarrollo de pedidos

**⏱️ ESTIMACIÓN:** 8 horas  
**🏷️ PRIORIDAD:** 🟠 MEDIA

---

## 📋 DÍA 5 - FINANCE (Pagos) + ANALYTICS (Base)

### 📋 TÍTULO: [Finance] - Pagos + Integración Commerce

**📝 DESCRIPCIÓN:**
- Objetivo: Completar Finance con pagos vinculados a pedidos
- Modelos: PaymentRecord
- Endpoints: Pagos, resumen financiero
- Lógica de negocio: Vinculación pagos-pedidos, estados financieros
- Permisos: Administrador, Ventas (pagos), otros (lectura)

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `finance/models.py`: Agregar PaymentRecord
   - `finance/serializers.py`: PaymentSerializer
   - `finance/views.py`: PaymentViewSet, FinancialSummaryView
   - `finance/urls.py`: Agregar /payments/, /summary/
   - `finance/services.py`: PaymentService, FinancialReportService

2. **Funcionalidades implementadas:**
   - Registro de pagos vinculados a pedidos
   - Resumen financiero por período
   - Estados de cuenta por cliente

3. **Tests mínimos:**
   - Test registro pagos
   - Test resumen financiero

4. **Dependencias resueltas:**
   - Commerce.Order disponible

**⏱️ ESTIMACIÓN:** 3 horas  
**🏷️ PRIORIDAD:** 🟠 MEDIA

### 📋 TÍTULO: [Analytics] - Dashboard + Métricas Base

**📝 DESCRIPCIÓN:**
- Objetivo: Dashboard básico con métricas principales
- Modelos: DashboardWidget, Metric, Notification (sistema de alertas del estudio)
- Endpoints: Widgets, métricas, KPIs
- Lógica de negocio: Cálculo métricas, widgets configurables
- Permisos: Todos los roles (métricas según permisos)

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `analytics/models.py`: DashboardWidget, Metric, Notification
   - `analytics/serializers.py`: WidgetSerializer, MetricSerializer, NotificationSerializer
   - `analytics/views.py`: DashboardViewSet, MetricViewSet, KPIView, NotificationViewSet
   - `analytics/urls.py`: /dashboard/, /metrics/, /kpis/, /notifications/
   - `analytics/services.py`: MetricCalculationService, DashboardService, NotificationService
   - `analytics/signals.py`: Generación automática de notificaciones

2. **Funcionalidades implementadas:**
   - Dashboard configurable por usuario
   - Métricas principales (ventas, gastos, desarrollo de pedidos)
   - KPIs en tiempo real
   - Sistema de notificaciones persistentes (stock bajo, mantenimiento equipos, pedidos)
   - Alertas automáticas por categoría de negocio fotográfico

3. **Tests mínimos:**
   - Test cálculo métricas
   - Test configuración dashboard
   - Test creación notificaciones automáticas
   - Test marcado como leída

4. **Dependencias resueltas:**
   - Todas las apps con datos básicos

**⏱️ ESTIMACIÓN:** 5 horas  
**🏷️ PRIORIDAD:** 🟢 BAJA

---

## 📋 DÍA 6 - ANALYTICS (Reportes) + INTEGRACIONES

### 📋 TÍTULO: [Analytics] - Sistema de Reportes + Exportación

**📝 DESCRIPCIÓN:**
- Objetivo: Sistema completo de reportes con exportación
- Modelos: Report, ReportExecution
- Endpoints: Reportes, ejecución, exportación PDF/Excel/CSV
- Lógica de negocio: Generación reportes, programación automática
- Permisos: Administrador (todo), otros según módulo

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `analytics/models.py`: Agregar Report, ReportExecution
   - `analytics/serializers.py`: ReportSerializer, ExecutionSerializer
   - `analytics/views.py`: ReportViewSet, ExecutionViewSet
   - `analytics/urls.py`: Agregar /reports/, /executions/
   - `analytics/services.py`: ReportGenerationService, ExportService
   - `analytics/exports.py`: PDFExport, ExcelExport, CSVExport

2. **Funcionalidades implementadas:**
   - Generación de reportes parametrizables
   - Exportación en múltiples formatos
   - Programación automática de reportes
   - Historial de ejecuciones

3. **Tests mínimos:**
   - Test generación reportes
   - Test exportación formatos
   - Test programación automática

4. **Dependencias resueltas:**
   - Todas las apps completamente funcionales

**⏱️ ESTIMACIÓN:** 6 horas  
**🏷️ PRIORIDAD:** 🟢 BAJA

### 📋 TÍTULO: [Integraciones] - APIs Cross-App + Validaciones

**📝 DESCRIPCIÓN:**
- Objetivo: Integrar todas las apps y validar funcionamiento conjunto
- Endpoints: APIs de integración entre módulos
- Lógica de negocio: Flujos completos end-to-end
- Permisos: Validación de permisos cross-app

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `integrations/services.py`: CrossAppService, ValidationService
   - `integrations/views.py`: IntegrationHealthView
   - `integrations/urls.py`: /health/, /integrations/

2. **Funcionalidades implementadas:**
   - Flujo completo: Cliente → Pedido → Producción → Pago
   - Validaciones de integridad entre apps
   - Health checks de todas las integraciones

3. **Tests mínimos:**
   - Test flujo end-to-end
   - Test integridad datos
   - Test health checks

4. **Dependencias resueltas:**
   - Todas las apps funcionales

**⏱️ ESTIMACIÓN:** 2 horas  
**🏷️ PRIORIDAD:** 🟠 MEDIA

---

## 📋 DÍA 7 - TESTING + DOCUMENTACIÓN

### 📋 TÍTULO: [Testing] - Tests de Integración + Performance

**📝 DESCRIPCIÓN:**
- Objetivo: Validar funcionamiento completo del sistema
- Tests: Integración, performance, carga, seguridad
- Lógica de negocio: Validación de todos los flujos
- Permisos: Testing completo del sistema de permisos

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `tests/integration/`: Tests de integración por módulo
   - `tests/performance/`: Tests de carga y performance
   - `tests/security/`: Tests de seguridad y permisos
   - `tests/fixtures/`: Datos de prueba para todos los módulos

2. **Funcionalidades implementadas:**
   - Suite completa de tests de integración
   - Tests de performance para endpoints críticos
   - Validación de seguridad multi-tenant
   - Coverage mínimo 80%

3. **Tests mínimos:**
   - Tests de integración para cada app
   - Tests de performance para APIs críticas
   - Tests de seguridad multi-tenant

4. **Dependencias resueltas:**
   - Sistema completamente funcional

**⏱️ ESTIMACIÓN:** 4 horas  
**🏷️ PRIORIDAD:** 🟡 ALTA

### 📋 TÍTULO: [Documentación] - API Docs + Deployment

**📝 DESCRIPCIÓN:**
- Objetivo: Documentación completa y preparación para deployment
- Documentación: API docs, README, guías de instalación
- Deployment: Configuración Docker, variables de entorno
- Lógica de negocio: Documentación de flujos de negocio

**✅ CRITERIOS DE ACEPTACIÓN:**

1. **Archivos a crear:**
   - `docs/api/`: Documentación completa de APIs
   - `docs/deployment/`: Guías de instalación y deployment
   - `docs/business/`: Documentación de flujos de negocio
   - `docker-compose.yml`: Configuración para desarrollo
   - `requirements.txt`: Dependencias del proyecto
   - `README.md`: Documentación principal

2. **Funcionalidades implementadas:**
   - Documentación automática con Swagger/OpenAPI
   - Guías de instalación paso a paso
   - Documentación de flujos de negocio
   - Configuración Docker lista para producción

3. **Tests mínimos:**
   - Validación de documentación actualizada
   - Test de instalación desde cero

4. **Dependencias resueltas:**
   - Sistema completamente funcional y testeado

**⏱️ ESTIMACIÓN:** 4 horas  
**🏷️ PRIORIDAD:** 🟢 BAJA

---

## 📊 Resumen del Sprint

### 📈 Métricas del Sprint

| Métrica | Valor | Objetivo |
|---------|-------|----------|
| **Total Horas** | 56h | 56h |
| **Apps Completadas** | 6 | 6 |
| **Modelos Implementados** | 24 | 24 |
| **Endpoints Creados** | ~60 | ~60 |
| **Tests Mínimos** | ~50 | ~50 |
| **Coverage Objetivo** | 80% | 80% |

### 🎯 Entregables Finales

1. ✅ **Backend Completamente Funcional**
   - 6 apps Django implementadas
   - Sistema multi-tenant operativo
   - Autenticación JWT funcional
   - Permisos granulares implementados

2. ✅ **APIs REST Completas**
   - ~60 endpoints documentados
   - Serializers con validaciones
   - Filtros y paginación
   - Exportación en múltiples formatos

3. ✅ **Sistema de Testing**
   - Tests unitarios por app
   - Tests de integración
   - Tests de performance
   - Coverage mínimo 80%

4. ✅ **Documentación Completa**
   - API documentation con Swagger
   - Guías de instalación
   - Documentación de flujos de negocio
   - README detallado

### 🚀 Preparado para Producción

Al final del sprint de 7 días, el backend estará **100% funcional** y listo para:
- Integración con frontend
- Deployment en producción
- Escalamiento horizontal
- Mantenimiento y evolución

---
*Sprint diseñado para máxima eficiencia y entrega de valor*