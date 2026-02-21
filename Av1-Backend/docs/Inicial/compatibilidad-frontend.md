# 🔗 Compatibilidad Frontend - Arte Ideas

## 🎯 Análisis del Frontend Actual

Basado en el análisis del código frontend React existente, este documento detalla las adaptaciones necesarias en el backend para garantizar 100% de compatibilidad.

## 📊 Frontend Stack Detectado

### Tecnologías Principales
```json
{
  "framework": "React 18.2.0",
  "router": "react-router-dom 6.26.2",
  "build": "Vite 7.1.6",
  "styling": "Tailwind CSS 3.4.13",
  "charts": "Recharts 2.12.7",
  "notifications": "react-toastify 11.0.5",
  "icons": "lucide-react 0.284.0",
  "pdf": "jspdf 3.0.2"
}
```

### Estructura de Rutas Frontend
```javascript
// Rutas principales detectadas en App.jsx
const FRONTEND_ROUTES = {
  AUTH: ['/', '/change-password', '/enviar-codigo', '/validar-codigo', '/nueva-contrasena'],
  MAIN: {
    dashboard: 'Dashboard',
    agenda: 'Agenda', 
    pedidos: 'Pedidos',
    clientes: 'Clientes',
    inventario: 'Inventario',
    activos: 'Activos',
    gastos: 'Gastos',
    produccion: 'Produccion',
    contratos: 'Contratos',
    reportes: 'Reportes',
    perfil: 'MiPerfil',
    configuracion: 'Configuracion'
  }
}
```

## 🔧 Adaptaciones Backend Requeridas

### 1. Estructura de APIs Esperadas

#### Base URL Configuration
```python
# settings.py - Configuración para el frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative dev port
]

# API Base URL esperada por frontend
API_BASE_URL = '/api'  # Según api.js del frontend
```

#### Endpoints Específicos del Frontend
```python
# urls.py - Estructura esperada por el frontend
urlpatterns = [
    # Autenticación (según authService.js)
    path('api/auth/login/', AuthLoginView.as_view()),
    path('api/auth/logout/', AuthLogoutView.as_view()),
    path('api/auth/refresh/', AuthRefreshView.as_view()),
    path('api/auth/profile/', AuthProfileView.as_view()),
    
    # Clientes (según clientesService.js)
    path('api/clients/', ClientListCreateView.as_view()),
    path('api/clients/<str:pk>/', ClientDetailView.as_view()),
    path('api/clients/search/', ClientSearchView.as_view()),
    
    # Pedidos (según pedidosService.js)
    path('api/orders/', OrderListCreateView.as_view()),
    path('api/orders/<str:pk>/', OrderDetailView.as_view()),
    path('api/orders/<str:pk>/status/', OrderStatusUpdateView.as_view()),
    
    # Inventario
    path('api/inventory/', InventoryListCreateView.as_view()),
    path('api/inventory/<str:pk>/', InventoryDetailView.as_view()),
    path('api/inventory/low-stock/', InventoryLowStockView.as_view()),
    
    # Producción
    path('api/production/', ProductionListCreateView.as_view()),
    path('api/production/<str:pk>/', ProductionDetailView.as_view()),
    path('api/production/<str:pk>/status/', ProductionStatusUpdateView.as_view()),
    
    # Contratos
    path('api/contracts/', ContractListCreateView.as_view()),
    path('api/contracts/<str:pk>/', ContractDetailView.as_view()),
    path('api/contracts/<str:pk>/download/', ContractDownloadView.as_view()),
    
    # Reportes
    path('api/reports/sales/', ReportSalesView.as_view()),
    path('api/reports/clients/', ReportClientsView.as_view()),
    path('api/reports/inventory/', ReportInventoryView.as_view()),
    path('api/reports/production/', ReportProductionView.as_view()),
    path('api/reports/export/', ReportExportView.as_view()),
    
    # Archivos
    path('api/files/upload/', FileUploadView.as_view()),
    path('api/files/<str:pk>/', FileDetailView.as_view()),
]
```

### 2. Modelos Adaptados al Frontend

#### Cliente Model (basado en Clientes.jsx)
```python
# crm/models.py
class Client(BaseModel):
    # Campos detectados en el frontend
    nombre = models.CharField(max_length=100)  # 'nombre' no 'name'
    tipo = models.CharField(max_length=20, choices=[
        ('Particular', 'Particular'),
        ('Colegio', 'Colegio'), 
        ('Empresa', 'Empresa'),
    ])
    contacto = models.CharField(max_length=15)  # 'contacto' no 'phone'
    email = models.EmailField(blank=True)
    ie = models.CharField(max_length=100, blank=True)  # Institución Educativa
    direccion = models.TextField(blank=True)  # 'direccion' no 'address'
    detalles = models.TextField(blank=True)  # Campo específico del frontend
    documento = models.CharField(max_length=20, blank=True)  # RUC/DNI
    
    # Campos calculados que espera el frontend
    fecha_registro = models.DateField(auto_now_add=True)
    ultimo_pedido = models.DateField(null=True, blank=True)
    total_pedidos = models.IntegerField(default=0)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'crm_client'
        unique_together = ['tenant', 'documento']
```

#### Order Model (basado en pedidosService.js)
```python
# commerce/models.py
class Order(BaseModel):
    # ID con formato específico esperado por frontend
    order_number = models.CharField(max_length=20, unique=True)  # PED + timestamp
    
    # Relaciones
    client = models.ForeignKey('crm.Client', on_delete=models.CASCADE)
    contrato_id = models.CharField(max_length=50, blank=True)  # Referencia a contrato
    
    # Campos específicos del frontend
    cliente = models.CharField(max_length=100)  # Nombre del cliente (desnormalizado)
    tipo = models.CharField(max_length=50)  # Tipo de producto/servicio
    descripcion = models.TextField(blank=True)
    producto_tipo = models.CharField(max_length=50, blank=True)
    
    # Fechas
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
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"PED{int(time.time() * 1000000) % 1000000}"
        super().save(*args, **kwargs)
```

### 3. Serializers Compatibles

#### Client Serializer
```python
# crm/serializers.py
class ClientSerializer(serializers.ModelSerializer):
    # Campos calculados que espera el frontend
    fechaRegistro = serializers.DateField(source='fecha_registro', read_only=True)
    ultimoPedido = serializers.DateField(source='ultimo_pedido', read_only=True)
    totalPedidos = serializers.IntegerField(source='total_pedidos', read_only=True)
    montoTotal = serializers.DecimalField(source='monto_total', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'nombre', 'tipo', 'contacto', 'email', 'ie', 
            'direccion', 'detalles', 'documento', 'fechaRegistro',
            'ultimoPedido', 'totalPedidos', 'montoTotal'
        ]
        
    def to_representation(self, instance):
        # Asegurar formato compatible con frontend
        data = super().to_representation(instance)
        
        # Generar ID con formato esperado (C + número)
        if not data['id'].startswith('C'):
            data['id'] = f"C{str(instance.pk).zfill(3)}"
            
        return data
```

#### Order Serializer
```python
# commerce/serializers.py
class OrderSerializer(serializers.ModelSerializer):
    # Campos con nombres específicos del frontend
    fechaCreacion = serializers.DateTimeField(source='fecha_creacion', read_only=True)
    fechaCompromiso = serializers.DateField(source='fecha_compromiso')
    fechaActualizacion = serializers.DateTimeField(source='fecha_actualizacion', read_only=True)
    productoTipo = serializers.CharField(source='producto_tipo')
    contratoId = serializers.CharField(source='contrato_id', required=False)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'cliente', 'tipo', 'descripcion',
            'fechaCreacion', 'fechaCompromiso', 'fechaActualizacion',
            'estado', 'avance', 'responsable', 'materiales',
            'productoTipo', 'contratoId', 'subtotal', 'tax', 'total'
        ]
```

### 4. Autenticación Compatible

#### Auth Views (basado en authService.js)
```python
# core/views.py
class AuthLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'success': False,
                'error': 'Por favor, completa todos los campos'
            }, status=400)
        
        user = authenticate(request, username=email, password=password)
        
        if user:
            # Verificar si es usuario nuevo que necesita cambiar contraseña
            if getattr(user, 'is_new_user', False):
                return Response({
                    'success': True,
                    'requiresPasswordChange': True,
                    'redirectTo': '/enviar-codigo',
                    'user': {
                        'id': str(user.id),
                        'name': user.get_full_name(),
                        'email': user.email,
                        'role': user.role,
                    }
                })
            
            # Login normal
            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'user': {
                    'id': str(user.id),
                    'name': user.get_full_name(),
                    'email': user.email,
                    'role': user.role,
                    'permissions': user.get_permissions_list(),
                },
                'token': str(refresh.access_token),
                'refresh': str(refresh),
            })
        
        return Response({
            'success': False,
            'error': 'Credenciales incorrectas'
        }, status=401)

class AuthProfileView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'success': True,
            'user': {
                'id': str(user.id),
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'permissions': user.get_permissions_list(),
                'profileImage': getattr(user, 'profile_image_url', None),
            }
        })
    
    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'user': serializer.data
            })
        
        return Response({
            'success': False,
            'error': 'Datos inválidos',
            'errors': serializer.errors
        }, status=400)
```

### 5. Sistema de Roles Compatible

#### User Model Adaptado (Específico para Estudio Fotográfico)
```python
# core/models.py
class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    
    # Roles específicos del frontend fotográfico
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('employee', 'Empleado'),
        ('photographer', 'Fotógrafo'),
        ('assistant', 'Asistente'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True)
    is_new_user = models.BooleanField(default=True)  # Para flujo cambio contraseña
    
    # Permisos específicos para estudio fotográfico
    def get_permissions_list(self):
        permission_map = {
            'admin': [
                'read:dashboard', 'write:orders', 'manage:clients', 
                'manage:users', 'access:configuration', 'manage:inventory',
                'manage:finances', 'view:reports', 'export:data',
                'manage:production', 'manage:assets', 'manage:contracts'
            ],
            'manager': [
                'read:dashboard', 'write:orders', 'manage:clients',
                'manage:inventory', 'view:reports', 'export:data',
                'manage:production', 'view:finances'
            ],
            'employee': [
                'read:dashboard', 'write:orders', 'manage:clients',
                'view:inventory', 'view:production'
            ],
            'photographer': [
                'read:dashboard', 'write:orders', 'manage:clients',
                'manage:production', 'view:inventory', 'manage:sessions'
            ],
            'assistant': [
                'read:dashboard', 'manage:clients', 'view:orders',
                'view:inventory'
            ],
        }
        return permission_map.get(self.role, [])
    
    def can_access_configuration(self):
        return self.role == 'admin'
```

### 6. Constantes y Configuración

#### Constants Compatibility
```python
# core/constants.py - Basado en constants.js del frontend

# Estados de pedidos fotográficos (debe coincidir exactamente)
ORDER_STATUS_CHOICES = [
    ('Pendiente', 'Pendiente'),
    ('En Proceso', 'En Proceso'),
    ('Listo para Entrega', 'Listo para Entrega'),
    ('Entregado', 'Entregado'),
    ('Cancelado', 'Cancelado'),
]

# Estados de producción fotográfica
PRODUCTION_STATUS_CHOICES = [
    ('Pendiente', 'Pendiente'),
    ('En Proceso', 'En Proceso'),
    ('Terminado', 'Terminado'),
    ('Entregado', 'Entregado'),
]

# Estados de contratos de servicios fotográficos
CONTRACT_STATUS_CHOICES = [
    ('Activo', 'Activo'),
    ('Pendiente', 'Pendiente'),
    ('Pagado', 'Pagado'),
    ('Vencido', 'Vencido'),
    ('Completado', 'Completado'),
]

# Tipos de clientes del estudio fotográfico
CLIENT_TYPE_CHOICES = [
    ('Particular', 'Particular'),
    ('Colegio', 'Colegio'),
    ('Empresa', 'Empresa'),
]

# Servicios fotográficos disponibles (según frontend)
SERVICES_CHOICES = [
    ('Impresión Digital', 'Impresión Digital'),
    ('Fotografía Escolar', 'Fotografía Escolar'),
    ('Promoción Escolar', 'Promoción Escolar'),
    ('Enmarcado', 'Enmarcado'),
    ('Retoque Fotográfico', 'Retoque Fotográfico'),
    ('Recordatorios', 'Recordatorios'),
    ('Ampliaciones', 'Ampliaciones'),
    ('Fotografía de Eventos', 'Fotografía de Eventos'),
    ('Sesión Familiar', 'Sesión Familiar'),
]

# Categorías de inventario especializado (según frontend)
INVENTORY_CATEGORIES = [
    ('enmarcados', 'Enmarcados'),
    ('minilab', 'Minilab'),
    ('graduaciones', 'Graduaciones'),
    ('corte_laser', 'Corte Láser'),
]

# Subcategorías de enmarcados (según frontend)
ENMARCADOS_SUBCATEGORIES = [
    ('molduras-listones', 'Moldura (Listón)'),
    ('molduras-prearmadas', 'Moldura Prearmada'),
    ('vidrios-tapas', 'Vidrio o Tapa MDF'),
    ('paspartu', 'Paspartú'),
]

# Estados de gastos
EXPENSE_STATUS_CHOICES = [
    ('Pendiente', 'Pendiente'),
    ('Pagado', 'Pagado'),
    ('Vencido', 'Vencido'),
]

# Tipos de gastos de servicios
SERVICE_EXPENSE_TYPES = [
    ('Alquiler', 'Alquiler'),
    ('Luz', 'Luz'),
    ('Agua', 'Agua'),
    ('Internet', 'Internet'),
    ('Teléfono', 'Teléfono'),
    ('Gas', 'Gas'),
]
```

### 7. Middleware de Compatibilidad

#### CORS y Headers
```python
# core/middleware.py
class FrontendCompatibilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Headers específicos para el frontend React
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, X-Tenant-ID'
            
        return response
```

### 8. Notificaciones Sistema

#### Notification Service Backend
```python
# analytics/models.py
class Notification(BaseModel):
    # Estructura compatible con notificationService.js
    title = models.CharField(max_length=200)
    message = models.TextField()
    description = models.TextField(blank=True)
    
    TYPE_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    
    CATEGORY_CHOICES = [
        ('inventory', 'Inventory'),
        ('maintenance', 'Maintenance'),
        ('order', 'Order'),
        ('client', 'Client'),
        ('production', 'Production'),
        ('contract', 'Contract'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    action = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict)
    
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
```

## 📋 Checklist de Compatibilidad

### ✅ APIs y Endpoints
- [ ] Estructura de URLs compatible con api.js
- [ ] Respuestas JSON con formato esperado por frontend
- [ ] Códigos de estado HTTP correctos
- [ ] Manejo de errores compatible con ApiError class

### ✅ Autenticación
- [ ] Login response compatible con authService.js
- [ ] JWT tokens en formato esperado
- [ ] Sistema de roles y permisos compatible
- [ ] Flujo de cambio de contraseña implementado

### ✅ Modelos de Datos
- [ ] Campos con nombres exactos del frontend
- [ ] Tipos de datos compatibles
- [ ] Choices/opciones idénticas
- [ ] IDs con formato esperado (C001, PED123456, etc.)

### ✅ Serializers
- [ ] Campos serializados con nombres correctos
- [ ] Campos calculados incluidos
- [ ] Formato de fechas compatible
- [ ] Relaciones anidadas según necesidad

### ✅ Configuración
- [ ] CORS configurado para Vite dev server
- [ ] Headers de respuesta correctos
- [ ] Timeouts compatibles con frontend
- [ ] Variables de entorno alineadas

---
*Documentación de compatibilidad para integración perfecta con el frontend React existente*