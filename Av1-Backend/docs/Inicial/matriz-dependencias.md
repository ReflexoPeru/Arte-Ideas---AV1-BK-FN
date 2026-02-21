# 🔗 Matriz de Dependencias - Arte Ideas

## 📊 Tabla de Dependencias

| App Backend | Depende de | Nivel | Prioridad Desarrollo | Desarrollo Paralelo |
|-------------|------------|-------|---------------------|-------------------|
| **Core** | - | 0 | 🔴 **CRÍTICA** | ❌ No (base de todo) |
| **CRM** | Core | 1 | 🟡 **ALTA** | ✅ Sí (independiente) |
| **Commerce** | Core, CRM | 2 | 🟡 **ALTA** | ❌ No (requiere CRM) |
| **Operations** | Core, Commerce | 2 | 🟠 **MEDIA** | ❌ No (requiere Commerce) |
| **Finance** | Core, Commerce | 2 | 🟠 **MEDIA** | ✅ Sí (parcialmente) |
| **Analytics** | Todas | 3 | 🟢 **BAJA** | ❌ No (requiere datos) |

## 🎯 Orden de Desarrollo Recomendado

### 📅 Secuencia Óptima

```
Día 1: Core (Base fundamental)
├── Autenticación JWT
├── Multi-tenancy
├── Usuarios y roles
└── Configuración básica

Día 2: CRM (Independiente de Commerce)
├── Clientes
├── Agenda
└── Contratos

Día 3: Commerce (Requiere CRM para clientes)
├── Productos
├── Inventario
└── Pedidos

Día 4: Operations (Requiere Commerce para pedidos de servicios)
├── Activos
├── Producción
└── Mantenimiento

Día 5: Finance (Requiere Commerce para pagos)
├── Gastos
├── Presupuestos
└── Pagos

Día 6-7: Analytics (Requiere todas para métricas)
├── Dashboard
├── Reportes
└── KPIs
```

## 🔄 Análisis de Dependencias Detallado

### 1. 🔐 Core App (Nivel 0)
**Dependencias:** Ninguna  
**Es requerida por:** TODAS las apps  
**Razón:** Base del sistema multi-tenant y autenticación  

```python
# Modelos que otras apps referencian:
- Tenant (FK en todos los modelos)
- User (FK para created_by, assigned_to, etc.)
- Role (para permisos)
```

**⚠️ CRÍTICO:** Debe completarse PRIMERO, bloquea todo el desarrollo.

---

### 2. 👥 CRM App (Nivel 1)
**Dependencias:** Core  
**Es requerida por:** Commerce, Analytics  
**Razón:** Los clientes son necesarios para pedidos  

```python
# Dependencias específicas:
from core.models import Tenant, User

# Modelos que otras apps referencian:
- Client (FK en Order, Contract)
```

**✅ INDEPENDIENTE:** Puede desarrollarse en paralelo con otras apps nivel 1.

---

### 3. 🛒 Commerce App (Nivel 2)
**Dependencias:** Core, CRM  
**Es requerida por:** Operations, Finance, Analytics  
**Razón:** Productos y pedidos son base de producción y finanzas  

```python
# Dependencias específicas:
from core.models import Tenant, User
from crm.models import Client

# Modelos que otras apps referencian:
- Order (FK en ProductionOrder, PaymentRecord)
- Registro de materiales (consulta para desarrollo de pedidos)
```

**⚠️ BLOQUEANTE:** Muchas apps dependen de Commerce.

---

### 4. ⚙️ Operations App (Nivel 2)
**Dependencias:** Core, Commerce  
**Es requerida por:** Analytics  
**Razón:** Desarrollo de pedidos se basa en órdenes de servicios del Commerce  

```python
# Dependencias específicas:
from core.models import Tenant, User
from commerce.models import Product, Order

# Modelos que otras apps referencian:
- Asset (para reportes de activos)
- ProductionOrder (para métricas de producción)
```

**✅ PARALELO PARCIAL:** Puede iniciarse con Commerce en desarrollo.

---

### 5. 💰 Finance App (Nivel 2)
**Dependencias:** Core, Commerce (opcional)  
**Es requerida por:** Analytics  
**Razón:** Pagos se relacionan con pedidos, pero gastos son independientes  

```python
# Dependencias específicas:
from core.models import Tenant, User
from commerce.models import Order  # Solo para PaymentRecord

# Modelos independientes:
- Expense (no requiere Commerce)
- ExpenseCategory (no requiere Commerce)
- Budget (no requiere Commerce)
```

**✅ PARALELO:** Gastos pueden desarrollarse independientemente.

---

### 6. 📊 Analytics App (Nivel 3)
**Dependencias:** TODAS las apps  
**Es requerida por:** Ninguna  
**Razón:** Consume datos de todas las apps para métricas  

```python
# Dependencias específicas:
from core.models import Tenant, User
from crm.models import Client, Appointment, Contract
from commerce.models import Product, Order
from operations.models import Asset, ProductionOrder
from finance.models import Expense, PaymentRecord
```

**❌ NO PARALELO:** Debe ser la última en desarrollarse.

## 🚧 Dependencias Críticas Identificadas

### 🔴 Dependencias Duras (Bloqueantes)
1. **Core → TODAS**: Sin Core no funciona nada
2. **CRM.Client → Commerce.Order**: Sin clientes no hay pedidos
3. **Commerce.Order → Operations.ProductionOrder**: Sin pedidos de servicios no hay órdenes de desarrollo/elaboración
4. **Commerce.Order → Finance.PaymentRecord**: Sin pedidos no hay pagos

### 🟡 Dependencias Blandas (Opcionales)
1. **Commerce.Order → Operations.ProductionOrder**: Desarrollo de pedidos puede ser independiente
2. **Operations.Asset → Finance.Expense**: Gastos de mantenimiento son opcionales
3. **Todas → Analytics**: Reportes pueden funcionar con datos parciales

## 📈 Estrategia de Desarrollo Paralelo

### 🟢 Apps que SÍ pueden desarrollarse en paralelo:

#### Día 2-3: CRM + Finance (parcial)
```
CRM: Clientes, Agenda, Contratos
Finance: Gastos, Categorías, Presupuestos
(Sin PaymentRecord que requiere Commerce)
```

#### Día 4-5: Commerce + Operations (inicio)
```
Commerce: Inventario fotográfico, Pedidos de servicios
Operations: Activos fotográficos, Mantenimiento
(Sin ProductionOrder que requiere pedidos de servicios)
```

### 🔴 Apps que NO pueden desarrollarse en paralelo:

#### Commerce → Operations (ProductionOrder)
- ProductionOrder requiere Order (pedido de servicio fotográfico)
- Debe esperar a que Commerce esté funcional

#### Cualquier app → Analytics
- Analytics requiere datos de todas las apps
- Debe ser la última en desarrollarse

## 🎯 Plan de Mitigación de Riesgos

### Riesgo 1: Core se retrasa
**Impacto:** Bloquea todo el desarrollo  
**Mitigación:** 
- Prioridad máxima en Core
- Equipo dedicado exclusivamente
- Testing continuo

### Riesgo 2: Commerce se retrasa
**Impacto:** Bloquea Operations y Finance  
**Mitigación:**
- Desarrollar Finance (gastos) independientemente
- Crear mocks de Commerce para Operations
- Interfaces bien definidas

### Riesgo 3: Dependencias circulares
**Impacto:** Código acoplado y difícil de mantener  
**Mitigación:**
- Revisión de arquitectura constante
- Interfaces claras entre apps
- Evitar imports cruzados

## 📋 Checklist de Dependencias

### ✅ Antes de iniciar cada app:

#### CRM
- [ ] Core.Tenant implementado
- [ ] Core.User implementado
- [ ] Autenticación JWT funcional

#### Commerce
- [ ] CRM.Client implementado
- [ ] Core completamente funcional
- [ ] Tests de CRM pasando

#### Operations
- [ ] Commerce.Order implementado (requerido para ProductionOrder)
- [ ] Commerce inventario fotográfico implementado
- [ ] Core y CRM estables

#### Finance
- [ ] Core completamente funcional
- [ ] Commerce.Order implementado (solo para PaymentRecord)
- [ ] Puede iniciarse sin Commerce para gastos

#### Analytics
- [ ] TODAS las apps implementadas
- [ ] APIs de todas las apps estables
- [ ] Datos de prueba disponibles

---
*Matriz diseñada para optimizar el flujo de desarrollo y minimizar bloqueos*