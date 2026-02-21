# 📦 Aplicaciones Backend - Arte Ideas

## 1. 🔐 Core App

**Módulos Frontend:** Mi Perfil, Configuración  
**Responsabilidad:** Autenticación, gestión de usuarios, configuración del sistema y multi-tenancy  

### Modelos Principales
```python
# models.py
class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    settings = models.JSONField(default=dict)

class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    is_tenant_admin = models.BooleanField(default=False)

class Role(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    permissions = models.JSONField(default=dict)
    is_system_role = models.BooleanField(default=False)

class SystemConfiguration(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    module = models.CharField(max_length=50)
    settings = models.JSONField(default=dict)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

### Endpoints Principales (Compatible con Frontend)
- `POST /api/auth/login/` - Autenticación JWT (formato específico)
- `POST /api/auth/logout/` - Cerrar sesión
- `POST /api/auth/refresh/` - Renovar token
- `GET/PUT /api/auth/profile/` - Perfil de usuario
- `GET/PUT /api/configuration/` - Configuración del sistema
- `GET /api/roles/` - Roles disponibles
- `POST /api/tenants/` - Crear tenant (super admin)

**Dependencias:** Ninguna (app base)

---

## 2. 👥 CRM App

**Módulos Frontend:** Clientes, Agenda, Contratos  
**Responsabilidad:** Gestión de relaciones con clientes, citas y documentos legales  

### Modelos Principales
```python
# models.py - Adaptado al frontend React existente
class Client(BaseModel):
    # Campos específicos del frontend (nombres exactos)
    nombre = models.CharField(max_length=100)  # 'nombre' según frontend
    tipo = models.CharField(max_length=20, choices=[
        ('Particular', 'Particular'),
        ('Colegio', 'Colegio'), 
        ('Empresa', 'Empresa'),
    ])
    contacto = models.CharField(max_length=15)  # 'contacto' según frontend
    email = models.EmailField(blank=True)
    ie = models.CharField(max_length=100, blank=True)  # Institución Educativa
    direccion = models.TextField(blank=True)  # 'direccion' según frontend
    detalles = models.TextField(blank=True)  # Campo específico del frontend
    documento = models.CharField(max_length=20, blank=True)  # RUC/DNI
    
    # Campos calculados que espera el frontend
    fecha_registro = models.DateField(auto_now_add=True)
    ultimo_pedido = models.DateField(null=True, blank=True)
    total_pedidos = models.IntegerField(default=0)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)

class Appointment(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES)
    assigned_to = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)

class Contract(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES)
    document = models.FileField(upload_to='contracts/', blank=True)
```

### Endpoints Principales (Compatible con Frontend)
- `GET/POST /api/clients/` - Listar/crear clientes
- `GET/PUT/DELETE /api/clients/{id}/` - CRUD cliente específico
- `GET /api/clients/search/` - Búsqueda de clientes (requerido por frontend)
- `GET/POST /api/appointments/` - Listar/crear citas
- `GET /api/appointments/calendar/` - Vista calendario
- `GET/POST /api/contracts/` - Listar/crear contratos
- `GET /api/contracts/{id}/download/` - Descargar contrato (según frontend)

**Dependencias:** Core (usuarios, tenant)

---

## 3. 🛒 Commerce App

**Módulos Frontend:** Pedidos, Inventario  
**Responsabilidad:** Gestión de pedidos fotográficos y registro manual de materiales en almacén (enmarcados, minilab, graduaciones, corte láser)  

### Modelos Principales
```python
# models.py
class Product(BaseModel):
    # Campos específicos para registro de materiales fotográficos
    nombre = models.CharField(max_length=100)  # 'nombre' según frontend
    categoria = models.CharField(max_length=50, choices=[
        ('enmarcados', 'Enmarcados'),
        ('minilab', 'Minilab'),
        ('graduaciones', 'Graduaciones'),
        ('corte_laser', 'Corte Láser'),
    ])
    subcategoria = models.CharField(max_length=50, blank=True)
    
    # Campos de registro de materiales (control manual)
    stock = models.IntegerField(default=0)  # 'stock' según frontend
    stock_minimo = models.IntegerField(default=0)  # 'stockMinimo' según frontend
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # 'precio' según frontend
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Campos específicos por categoría (JSON para flexibilidad)
    propiedades = models.JSONField(default=dict)  # width, color, material, etc.
    
    # Campos adicionales del frontend
    proveedor = models.CharField(max_length=100, blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

class Order(BaseModel):
    # ID con formato específico esperado por frontend
    order_number = models.CharField(max_length=20, unique=True)  # PED + timestamp
    
    # Relaciones
    client = models.ForeignKey('crm.Client', on_delete=models.CASCADE)
    contrato_id = models.CharField(max_length=50, blank=True)  # Referencia a contrato
    
    # Campos específicos del frontend fotográfico
    cliente = models.CharField(max_length=100)  # Nombre del cliente (desnormalizado)
    servicio = models.CharField(max_length=50, choices=[
        ('Impresión Digital', 'Impresión Digital'),
        ('Fotografía Escolar', 'Fotografía Escolar'),
        ('Promoción Escolar', 'Promoción Escolar'),
        ('Enmarcado', 'Enmarcado'),
        ('Retoque Fotográfico', 'Retoque Fotográfico'),
        ('Recordatorios', 'Recordatorios'),
        ('Ampliaciones', 'Ampliaciones'),
        ('Fotografía de Eventos', 'Fotografía de Eventos'),
        ('Sesión Familiar', 'Sesión Familiar'),
    ])
    cantidad = models.IntegerField(default=1)  # 'cantidad' según frontend
    especificaciones = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    
    # Fechas (nombres según frontend)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_compromiso = models.DateField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Estado y progreso
    estado = models.CharField(max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Listo para Entrega', 'Listo para Entrega'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ], default='Pendiente')
    avance = models.IntegerField(default=0)  # Porcentaje 0-100
    
    # Responsable y materiales
    responsable = models.CharField(max_length=100, blank=True)
    materiales = models.JSONField(default=list)
    
    # Montos (según frontend)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # 'precio' según frontend
    adelanto = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 'adelanto' según frontend
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # calculado
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

class StockMovement(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField()
    reference_id = models.CharField(max_length=50, blank=True)  # Order ID, etc.
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
```

### Endpoints Principales (Compatible con Frontend)
- `GET/POST /api/products/` - Listar/crear productos
- `GET/POST /api/inventory/` - Gestión de inventario (según frontend)
- `GET /api/inventory/low-stock/` - Productos con stock bajo
- `GET/POST /api/orders/` - Listar/crear pedidos
- `PUT /api/orders/{id}/status/` - Actualizar estado pedido (según frontend)
- `GET /api/inventory/movements/` - Movimientos de stock
- `POST /api/inventory/adjust/` - Ajustar inventario

**Dependencias:** Core (usuarios, tenant), CRM (clientes)

---

## 4. ⚙️ Operations App

**Módulos Frontend:** Producción, Activos  
**Responsabilidad:** Gestión del desarrollo/elaboración de pedidos de clientes (marcos, impresiones, etc.) y activos del estudio (equipos, cámaras, impresoras)  

### Modelos Principales
```python
# models.py
class Asset(BaseModel):
    # Campos específicos para activos fotográficos
    nombre = models.CharField(max_length=100)  # 'nombre' según frontend
    categoria = models.CharField(max_length=50, choices=[
        ('Impresora', 'Impresora'),
        ('Equipo_oficina', 'Equipo de Oficina'),
        ('Maquinaria', 'Maquinaria'),
        ('Camara', 'Cámara Fotográfica'),
        ('Iluminacion', 'Equipo de Iluminación'),
    ])
    proveedor = models.CharField(max_length=100)
    fecha_compra = models.DateField()  # 'fechaCompra' según frontend
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)  # 'costoTotal' según frontend
    tipo_pago = models.CharField(max_length=20, choices=[
        ('Contado', 'Contado'),
        ('Financiado', 'Financiado'),
        ('Leasing', 'Leasing'),
    ])
    vida_util = models.IntegerField()  # en meses
    depreciacion = models.DecimalField(max_digits=10, decimal_places=2)  # mensual
    estado = models.CharField(max_length=20, choices=[
        ('Activo', 'Activo'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Inactivo', 'Inactivo'),
    ], default='Activo')

class ProductionOrder(BaseModel):
    # Campos específicos para desarrollo/elaboración de pedidos
    numero_op = models.CharField(max_length=20, unique=True)  # 'numeroOP' según frontend
    pedido = models.CharField(max_length=20)  # Referencia al pedido
    cliente = models.CharField(max_length=100)  # 'cliente' según frontend
    descripcion = models.TextField()  # 'descripcion' según frontend
    tipo = models.CharField(max_length=50, choices=[
        ('Graduación', 'Graduación'),
        ('Enmarcado', 'Enmarcado'),
        ('Minilab', 'Minilab'),
        ('Corte Láser', 'Corte Láser'),
        ('Sesión Fotográfica', 'Sesión Fotográfica'),
    ])
    estado = models.CharField(max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Terminado', 'Terminado'),
        ('Entregado', 'Entregado'),
    ], default='Pendiente')
    prioridad = models.CharField(max_length=20, choices=[
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Normal', 'Normal'),
        ('Baja', 'Baja'),
    ], default='Normal')
    operario = models.CharField(max_length=100)  # 'operario' según frontend
    fecha_estimada = models.DateField()  # 'fechaEstimada' según frontend

class ProductionTask(models.Model):
    production_order = models.ForeignKey(ProductionOrder, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sequence_order = models.IntegerField()
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES)
    assigned_to = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    assets_used = models.ManyToManyField(Asset, blank=True)

class MaintenanceRecord(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance_date = models.DateField()
    next_maintenance_date = models.DateField(null=True, blank=True)
    performed_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
```

### Endpoints Principales (Compatible con Frontend)
- `GET/POST /api/assets/` - Listar/crear activos
- `GET /api/assets/maintenance-due/` - Activos con mantenimiento pendiente
- `GET/POST /api/production/` - Órdenes de producción (según frontend)
- `PUT /api/production/{id}/status/` - Actualizar estado producción (según frontend)
- `GET/POST /api/production/tasks/` - Tareas de producción
- `POST /api/maintenance/` - Registrar mantenimiento

**Dependencias:** Core (usuarios, tenant), Commerce (pedidos de servicios fotográficos)

---

## 5. 💰 Finance App

**Módulos Frontend:** Gastos  
**Responsabilidad:** Gestión financiera del estudio fotográfico, control de gastos operativos (personal, servicios, insumos)  

### Modelos Principales
```python
# models.py
class ExpenseCategory(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

# Gastos de Personal
class PersonalExpense(BaseModel):
    codigo = models.CharField(max_length=20, unique=True)  # 'codigo' según frontend
    nombre = models.CharField(max_length=100)  # 'nombre' según frontend
    cargo = models.CharField(max_length=50)  # 'cargo' según frontend
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)  # 'salarioBase' según frontend
    bonificaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_pago = models.DateField(null=True, blank=True)  # 'fechaPago' según frontend
    estado = models.CharField(max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('Pagado', 'Pagado'),
    ], default='Pendiente')

# Gastos de Servicios
class ServiceExpense(BaseModel):
    codigo = models.CharField(max_length=20, unique=True)  # 'codigo' según frontend
    tipo = models.CharField(max_length=50, choices=[
        ('Alquiler', 'Alquiler'),
        ('Luz', 'Luz'),
        ('Agua', 'Agua'),
        ('Internet', 'Internet'),
        ('Teléfono', 'Teléfono'),
        ('Gas', 'Gas'),
    ])
    proveedor = models.CharField(max_length=100)  # 'proveedor' según frontend
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # 'monto' según frontend
    fecha_vencimiento = models.DateField()  # 'fechaVenc' según frontend
    fecha_pago = models.DateField(null=True, blank=True)  # 'fechaPago' según frontend
    periodo = models.CharField(max_length=50)  # 'periodo' según frontend
    estado = models.CharField(max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('Pagado', 'Pagado'),
        ('Vencido', 'Vencido'),
    ], default='Pendiente')

class Budget(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    budgeted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)

class PaymentRecord(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    order = models.ForeignKey('commerce.Order', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
```

### Endpoints Principales
- `GET/POST /api/expenses/` - Listar/crear gastos
- `POST /api/expenses/{id}/approve/` - Aprobar gasto
- `GET /api/expenses/categories/` - Categorías de gastos
- `GET/POST /api/budgets/` - Presupuestos
- `GET /api/finance/summary/` - Resumen financiero
- `POST /api/payments/` - Registrar pagos

**Dependencias:** Core (usuarios, tenant), Commerce (pedidos para pagos)

---

## 6. 📊 Analytics App

**Módulos Frontend:** Dashboard, Reportes  
**Responsabilidad:** Métricas, análisis de datos y generación de reportes  

### Modelos Principales
```python
# models.py
class DashboardWidget(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

class Report(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)

class ReportExecution(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    executed_at = models.DateTimeField(auto_now_add=True)
    executed_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    parameters_used = models.JSONField(default=dict)
    file_path = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=EXECUTION_STATUS_CHOICES)
    error_message = models.TextField(blank=True)

class Metric(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    metric_type = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(BaseModel):
    # Sistema de notificaciones persistentes del estudio
    title = models.CharField(max_length=200)
    message = models.TextField()
    description = models.TextField(blank=True)
    
    # Tipos específicos del estudio fotográfico
    type = models.CharField(max_length=20, choices=[
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ], default='info')
    
    # Categorías del negocio fotográfico
    category = models.CharField(max_length=20, choices=[
        ('inventory', 'Stock de materiales'),
        ('maintenance', 'Mantenimiento equipos'),
        ('order', 'Pedidos de servicios'),
        ('client', 'Gestión de clientes'),
        ('production', 'Desarrollo de pedidos'),
        ('contract', 'Contratos de servicios'),
    ])
    
    action = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Endpoints Principales
- `GET /api/dashboard/widgets/` - Widgets del dashboard
- `POST /api/dashboard/widgets/` - Crear widget personalizado
- `GET /api/dashboard/metrics/` - Métricas principales
- `GET/POST /api/reports/` - Listar/crear reportes
- `POST /api/reports/{id}/execute/` - Ejecutar reporte
- `GET /api/reports/executions/` - Historial de ejecuciones
- `GET /api/analytics/kpis/` - KPIs principales
- `GET /api/notifications/` - Notificaciones del usuario
- `POST /api/notifications/` - Crear notificación
- `PUT /api/notifications/{id}/mark-read/` - Marcar como leída
- `POST /api/notifications/mark-all-read/` - Marcar todas como leídas
- `GET /api/notifications/unread-count/` - Contador no leídas

**Dependencias:** Todas las apps (para métricas, reportes y generación automática de notificaciones)

---

## 📋 Resumen de Modelos por App

| App | Modelos Principales | Total Modelos |
|-----|-------------------|---------------|
| **Core** | Tenant, User, Role, SystemConfiguration | 4 |
| **CRM** | Client, Appointment, Contract | 3 |
| **Commerce** | Product, Order, OrderItem, StockMovement | 4 |
| **Operations** | Asset, ProductionOrder, ProductionTask, MaintenanceRecord | 4 |
| **Finance** | Expense, ExpenseCategory, Budget, PaymentRecord | 4 |
| **Analytics** | DashboardWidget, Report, ReportExecution, Metric, Notification | 5 |
| **TOTAL** | | **24 modelos** |

---
*Diseño modular optimizado para escalabilidad y mantenimiento*