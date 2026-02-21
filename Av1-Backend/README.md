# 🎨 Arte Ideas - Backend Core App
xdd
Sistema multi-tenant para estudios fotográficos con gestión completa de usuarios, perfiles y configuraciones empresariales.

> **🆕 Actualización HU01:** Sistema de roles actualizado según especificaciones de negocio. Nuevos roles: Admin, Ventas, Producción, Operario.

## 📋 Tabla de Contenidos

- [🎯 Descripción](#-descripción)
- [🏗️ Arquitectura](#️-arquitectura)
- [🚀 Instalación](#-instalación)
- [📊 Modelos de Datos](#-modelos-de-datos)
- [🔌 API Endpoints](#-api-endpoints)
- [🧪 Testing con Postman](#-testing-con-postman)
- [🔐 Autenticación](#-autenticación)
- [🏢 Multi-Tenancy](#️-multi-tenancy)
- [👥 Roles y Permisos](#-roles-y-permisos)
- [📱 Uso](#-uso)
- [🛠️ Desarrollo](#️-desarrollo)

---

## 🎯 Descripción

**Arte Ideas Core App** es el módulo central de un sistema multi-tenant diseñado para estudios fotográficos. Proporciona:

- ✅ **Autenticación JWT** con refresh tokens
- ✅ **Sistema multi-tenant** con aislamiento de datos
- ✅ **Gestión de usuarios** con roles granulares
- ✅ **Perfiles personalizables** con estadísticas
- ✅ **Configuración empresarial** por tenant
- ✅ **Permisos granulares** por rol y módulo
- ✅ **API REST completa** con documentación

### 🎨 Características Principales

| Característica | Descripción |
|----------------|-------------|
| **Multi-Tenant** | Aislamiento completo de datos por estudio fotográfico |
| **Roles Granulares** | 5 roles HU01: Super Admin, Admin, Ventas, Producción, Operario |
| **JWT Authentication** | Tokens seguros con expiración y refresh automático |
| **Perfiles Dinámicos** | Gestión personal con estadísticas y actividad |
| **Configuración Flexible** | Configuración empresarial independiente por tenant |
| **API REST** | 26 endpoints documentados con ejemplos completos |

---

## 🏗️ Arquitectura

### 📁 Estructura del Proyecto

```
arte-ideas-backend/
├── 📁 apps/
│   └── 📁 core/                    # App principal
│       ├── 📁 authentication/      # Módulo de autenticación
│       ├── 📁 profile/             # Módulo de perfiles
│       ├── 📁 configuration/       # Módulo de configuración
│       ├── 📁 migrations/          # Migraciones de BD
│       ├── 📄 models.py            # Modelos de datos
│       ├── 📄 urls.py              # URLs principales
│       └── 📄 views.py             # Vistas base
├── 📁 config/                      # Configuración Django
├── 📁 shared/                      # Utilidades compartidas
├── 📁 docs/                        # Documentación técnica
├── 📄 API_ENDPOINTS_ARTE_IDEAS.md  # Documentación de API
├── 📄 Arte_Ideas_Core_API.postman_collection.json
├── 📄 Arte_Ideas_Core_Environment.postman_environment.json
└── 📄 requirements.txt
```

### 🔧 Tecnologías

- **Backend:** Django 4.2.7 + Django REST Framework
- **Base de Datos:** MySQL 8.0
- **Autenticación:** JWT (Simple JWT)
- **Documentación:** Markdown + Postman Collections
- **Testing:** Postman + Django Test Suite

---

## 🚀 Instalación

### 📋 Prerrequisitos

- Python 3.11+
- MySQL 8.0+
- Git

### ⚡ Setup Rápido

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd arte-ideas-backend

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos MySQL
# Crear base de datos: arte_ideas_db
# Usuario: root, Password: 12345

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Crear datos de prueba (opcional)
python manage.py shell -c "
from apps.core.models import Tenant, User
from django.contrib.auth.hashers import make_password

# Crear tenants
tenant_a = Tenant.objects.create(
    name='Estudio Fotográfico A',
    slug='tenant-a',
    business_name='Arte Ideas Diseño Gráfico A',
    business_address='Av. Lima 123, San Juan de Lurigancho',
    business_phone='987654321',
    business_email='info@tenant-a.com',
    business_ruc='20123456789',
    currency='PEN',
    location_type='lima',
    max_users=20,
    is_active=True
)

# Crear usuarios
User.objects.create(
    username='superadmin',
    email='admin@arteideas.com',
    first_name='Super',
    last_name='Admin',
    password=make_password('admin123'),
    role='super_admin',
    is_active=True,
    is_staff=True,
    is_superuser=True,
    email_verified=True
)

User.objects.create(
    username='admin_a',
    email='admin@tenant-a.com',
    first_name='Admin',
    last_name='Tenant A',
    password=make_password('admin123'),
    role='admin',
    tenant=tenant_a,
    is_active=True,
    is_staff=True,
    email_verified=True
)
"

# 7. Iniciar servidor
python manage.py runserver
```

### ✅ Verificación

```bash
# Health check
curl http://localhost:8000/api/core/health/

# Respuesta esperada:
{
  "status": "ok",
  "message": "Arte Ideas Core App funcionando correctamente"
}
```

---

## 📊 Modelos de Datos

### 🏢 Tenant (Estudios Fotográficos)

```python
class Tenant(models.Model):
    id = models.AutoField(primary_key=True)  # ID simple: 1, 2, 3...
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    business_name = models.CharField(max_length=200)
    business_address = models.TextField()
    business_phone = models.CharField(max_length=15)
    business_email = models.EmailField()
    business_ruc = models.CharField(max_length=11)
    currency = models.CharField(max_length=10, choices=[...])
    location_type = models.CharField(max_length=20, choices=[...])
    max_users = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
```

**Campos Principales:**
- `name`: Nombre del estudio fotográfico
- `business_*`: Información empresarial completa
- `currency`: Moneda (PEN, USD, EUR)
- `location_type`: Tipo de ubicación (lima, provincia)
- `max_users`: Límite de usuarios por tenant

### 👤 User (Usuarios del Sistema)

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Administrador'),
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('employee', 'Empleado'),
        ('photographer', 'Fotógrafo'),
        ('assistant', 'Asistente'),
    ]
    
    id = models.AutoField(primary_key=True)  # ID simple: 1, 2, 3...
    tenant = models.ForeignKey(Tenant, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_new_user = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
```

**Roles Disponibles (HU01):**
- `super_admin`: Acceso completo a todos los tenants
- `admin`: Gestión completa dentro de su tenant (Administrador)
- `ventas`: Acceso a módulos de ventas (Clientes, Pedidos, Agenda, Contratos)
- `produccion`: Acceso a módulos de producción (Producción, Inventario, Activos)
- `operario`: Acceso básico operacional (Dashboard, Agenda, Producción - solo vista)

### 👤 UserProfile (Perfil Extendido)

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=[('es', 'Español'), ('en', 'English')])
    theme = models.CharField(max_length=10, choices=[('light', 'Claro'), ('dark', 'Oscuro')])
    email_notifications = models.BooleanField(default=True)
```

### 📊 UserActivity (Registro de Actividad)

```python
class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('create', 'Crear registro'),
        ('update', 'Actualizar registro'),
        ('delete', 'Eliminar registro'),
        ('export', 'Exportar datos'),
        ('config_change', 'Cambio de configuración'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    module = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 🔐 RolePermission (Permisos por Rol)

```python
class RolePermission(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    
    # Módulos con acceso
    access_dashboard = models.BooleanField(default=True)
    access_agenda = models.BooleanField(default=True)
    access_pedidos = models.BooleanField(default=True)
    access_clientes = models.BooleanField(default=True)
    access_inventario = models.BooleanField(default=False)
    access_activos = models.BooleanField(default=False)
    access_gastos = models.BooleanField(default=False)
    access_produccion = models.BooleanField(default=False)
    access_contratos = models.BooleanField(default=False)
    access_reportes = models.BooleanField(default=False)
    
    # Acciones sensibles
    view_costos = models.BooleanField(default=False)
    view_precios = models.BooleanField(default=False)
    view_margenes = models.BooleanField(default=False)
    view_datos_clientes = models.BooleanField(default=False)
    view_datos_financieros = models.BooleanField(default=False)
    edit_precios = models.BooleanField(default=False)
    delete_registros = models.BooleanField(default=False)
```

---

## 🔌 API Endpoints

### 📋 Resumen de Endpoints

| Módulo | Endpoints | Descripción |
|--------|-----------|-------------|
| **Autenticación** | 3 | Login, refresh token, logout |
| **Mi Perfil** | 7 | Gestión personal del usuario |
| **Configuración** | 16 | Gestión de usuarios, negocio y permisos |
| **Total** | **26** | Endpoints completamente documentados |

### 🔐 Autenticación (`/api/core/auth/`)

```http
POST /api/core/auth/login/          # Login de usuario
POST /api/core/auth/refresh/        # Refresh token
POST /api/core/auth/logout/         # Logout de usuario
```

### 👤 Mi Perfil (`/api/core/profile/`)

```http
GET  /api/core/profile/view/              # Ver mi perfil
PUT  /api/core/profile/edit/              # Editar mi perfil
GET  /api/core/profile/statistics/        # Estadísticas mensuales
GET  /api/core/profile/activity/          # Actividad reciente
GET  /api/core/profile/completion/        # Porcentaje completitud
POST /api/core/profile/change-password/   # Cambiar contraseña
POST /api/core/profile/change-email/      # Cambiar email
```

### ⚙️ Configuración (`/api/core/config/`)

#### Configuración del Negocio
```http
GET /api/core/config/business/view/       # Ver configuración del negocio
PUT /api/core/config/business/edit/       # Editar configuración del negocio
```

#### Gestión de Usuarios
```http
GET    /api/core/config/users/list/           # Lista de usuarios del tenant
POST   /api/core/config/users/create/         # Crear nuevo usuario
GET    /api/core/config/users/{id}/view/      # Ver usuario específico
PUT    /api/core/config/users/{id}/edit/      # Editar usuario
PATCH  /api/core/config/users/{id}/toggle/    # Activar/Desactivar usuario
DELETE /api/core/config/users/{id}/delete/    # Eliminar usuario
```

#### Roles y Permisos HU01
```http
GET  /api/core/config/roles/list/                    # Lista de roles disponibles (admin, ventas, produccion, operario)
GET  /api/core/config/permissions/{role}/view/       # Ver permisos de rol específico
PUT  /api/core/config/permissions/{role}/edit/       # Editar permisos de rol
POST /api/core/config/permissions/{role}/reset/      # Restablecer permisos por defecto

# Ejemplos específicos para roles HU01:
GET  /api/core/config/permissions/ventas/view/       # Ver permisos del rol Ventas
GET  /api/core/config/permissions/produccion/view/   # Ver permisos del rol Producción  
GET  /api/core/config/permissions/operario/view/     # Ver permisos del rol Operario
```

#### Super Admin - Gestión de Tenants
```http
GET  /api/core/config/tenants/list/           # Lista de todos los tenants
POST /api/core/config/tenants/create/         # Crear nuevo tenant
GET  /api/core/config/tenants/{id}/users/     # Usuarios de un tenant
```

### 🏥 Sistema
```http
GET /api/core/health/                         # Health check del sistema
```

---

## 🧪 Testing con Postman

### 📁 Archivos Incluidos

| Archivo | Descripción |
|---------|-------------|
| `Arte_Ideas_Core_API.postman_collection.json` | Colección completa de endpoints |
| `Arte_Ideas_Core_Environment.postman_environment.json` | Variables de entorno |
| `API_ENDPOINTS_ARTE_IDEAS.md` | Documentación completa con ejemplos |

### ⚡ Setup Rápido en Postman

1. **Importar Colección:**
   - Abrir Postman
   - Click "Import" → Seleccionar `Arte_Ideas_Core_API.postman_collection.json`

2. **Importar Environment:**
   - Click "Import" → Seleccionar `Arte_Ideas_Core_Environment.postman_environment.json`

3. **Activar Environment:**
   - Esquina superior derecha → Seleccionar "Arte Ideas Core - Development"

4. **Hacer Login:**
   - Ejecutar `POST Login` con credenciales
   - El token se guarda automáticamente

### 🔧 Variables de Entorno

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",                    // Se llena automáticamente
  "refresh_token": "",                   // Se llena automáticamente
  "superadmin_access_token": "",         // Para pruebas de super admin
  "user_id": "3",                        // Usuario de prueba
  "tenant_id": "1",                      // Tenant de prueba
  "role_code": "employee"                // Rol de prueba
}
```

### 🎯 Ejemplos de Uso

**Login Automático:**
```http
POST {{base_url}}/api/core/auth/login/
{
  "username": "admin_a",
  "password": "admin123"
}
```

**Usar Variables:**
```http
GET {{base_url}}/api/core/config/users/{{user_id}}/view/
Authorization: Bearer {{access_token}}
```

---

## 🔐 Autenticación

### 🎫 JWT Tokens

**Configuración:**
- **Access Token:** 8 horas de duración
- **Refresh Token:** 7 días de duración
- **Algoritmo:** HS256
- **Blacklist:** Tokens invalidados automáticamente

### 👥 Credenciales de Prueba

| Usuario | Password | Rol | Tenant |
|---------|----------|-----|--------|
| `superadmin` | `admin123` | Super Admin | Global |
| `admin_a` | `admin123` | Admin | Tenant 1 |
| `admin_b` | `admin123` | Admin | Tenant 2 |
| `user_a` | `user123` | Employee | Tenant 1 |
| `user_b` | `user123` | Employee | Tenant 2 |
| `fotografo_a` | `fotografo123` | Photographer | Tenant 1 |

### 🔒 Headers de Autenticación

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

---

## 🏢 Multi-Tenancy

### 🎯 Aislamiento de Datos

**Principios:**
- ✅ **Aislamiento completo** por tenant
- ✅ **Filtrado automático** en todas las consultas
- ✅ **Super admin** ve todos los tenants
- ✅ **Usuarios regulares** solo ven su tenant

### 🏗️ Estructura de Tenants

```python
# Tenant 1: Estudio Fotográfico A
{
  "id": 1,
  "name": "Estudio Fotográfico A",
  "slug": "tenant-a",
  "business_name": "Arte Ideas Diseño Gráfico A",
  "location_type": "lima",
  "max_users": 20
}

# Tenant 2: Estudio Fotográfico B
{
  "id": 2,
  "name": "Estudio Fotográfico B", 
  "slug": "tenant-b",
  "business_name": "Arte Ideas Diseño Gráfico B",
  "location_type": "provincia",
  "max_users": 10
}
```

### 🔍 Filtrado Automático

```python
# Los usuarios solo ven datos de su tenant
User.objects.filter(tenant=request.user.tenant)

# Super admin ve todos los datos
if request.user.role == 'super_admin':
    User.objects.all()
```

---

## 👥 Roles y Permisos

### 🎭 Jerarquía de Roles HU01

```
Super Admin (Global)
├── Admin (Tenant) - Administrador completo
├── Ventas (Tenant) - Gestión comercial y clientes
├── Producción (Tenant) - Gestión de producción e inventario
└── Operario (Tenant) - Acceso básico operacional
```

### 📋 Matriz de Permisos HU01

| Módulo | Super Admin | Admin | Ventas | Producción | Operario |
|--------|-------------|-------|--------|------------|----------|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Agenda | ✅ | ✅ | ✅ | ❌ | ✅ |
| Pedidos | ✅ | ✅ | ✅ | ✅ | ❌ |
| Clientes | ✅ | ✅ | ✅ | ❌ | ❌ |
| Inventario | ✅ | ✅ | ❌ | ✅ | ❌ |
| Activos | ✅ | ✅ | ❌ | ✅ | ❌ |
| Gastos | ✅ | ✅ | ❌ | ❌ | ❌ |
| Producción | ✅ | ✅ | ❌ | ✅ | ✅ |
| Contratos | ✅ | ✅ | ✅ | ❌ | ❌ |
| Reportes | ✅ | ✅ | ✅ | ✅ | ❌ |

### 🔐 Acciones Sensibles HU01

| Acción | Super Admin | Admin | Ventas | Producción | Operario |
|--------|-------------|-------|--------|------------|----------|
| Ver Costos | ✅ | ✅ | ❌ | ✅ | ❌ |
| Ver Precios | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver Márgenes | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver Datos Clientes | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver Datos Financieros | ✅ | ✅ | ❌ | ❌ | ❌ |
| Editar Precios | ✅ | ✅ | ❌ | ❌ | ❌ |
| Eliminar Registros | ✅ | ✅ | ❌ | ❌ | ❌ |

### 🎯 Descripción de Roles HU01

**🔴 Super Admin:**
- Acceso completo a todos los tenants
- Gestión de tenants y usuarios globales
- Todas las acciones sensibles habilitadas

**🟠 Admin (Administrador):**
- Gestión completa dentro de su tenant
- Acceso a todos los módulos y configuraciones
- Gestión de usuarios y permisos del tenant

**🟡 Ventas:**
- Enfoque en gestión comercial y relación con clientes
- Acceso a: Dashboard, Agenda, Pedidos, Clientes, Contratos, Reportes
- Puede ver precios y datos de clientes

**🟢 Producción:**
- Enfoque en operaciones de producción e inventario
- Acceso a: Dashboard, Producción, Inventario, Activos, Pedidos, Reportes
- Puede ver costos de materiales y producción

**🔵 Operario:**
- Acceso básico para tareas operacionales
- Acceso a: Dashboard, Agenda, Producción (solo vista)
- Sin acceso a información financiera o administrativa

---

## 📱 Uso

### 🚀 Flujo Básico de Usuario

1. **Login:**
   ```http
   POST /api/core/auth/login/
   {
     "username": "admin_a",
     "password": "admin123"
   }
   ```

2. **Ver Perfil:**
   ```http
   GET /api/core/profile/view/
   Authorization: Bearer <token>
   ```

3. **Gestionar Usuarios:**
   ```http
   GET /api/core/config/users/list/
   Authorization: Bearer <token>
   ```

### 🔧 Flujo de Administrador HU01

1. **Configurar Negocio:**
   ```http
   PUT /api/core/config/business/edit/
   {
     "business_name": "Mi Estudio Actualizado",
     "business_phone": "999888777"
   }
   ```

2. **Crear Usuario con Rol Ventas:**
   ```http
   POST /api/core/config/users/create/
   {
     "username": "vendedor1",
     "email": "ventas@empresa.com",
     "first_name": "Juan",
     "last_name": "Vendedor", 
     "role": "ventas",
     "password": "password123",
     "confirm_password": "password123"
   }
   ```

3. **Crear Usuario con Rol Producción:**
   ```http
   POST /api/core/config/users/create/
   {
     "username": "productor1",
     "email": "produccion@empresa.com",
     "first_name": "María",
     "last_name": "Productora",
     "role": "produccion", 
     "password": "password123",
     "confirm_password": "password123"
   }
   ```

4. **Verificar Permisos de Rol:**
   ```http
   GET /api/core/config/permissions/ventas/view/
   GET /api/core/config/permissions/produccion/view/
   GET /api/core/config/permissions/operario/view/
   ```

5. **Configurar Permisos Personalizados:**
   ```http
   PUT /api/core/config/permissions/ventas/edit/
   {
     "access_dashboard": true,
     "access_clientes": true,
     "access_pedidos": true,
     "access_contratos": true,
     "view_precios": true,
     "view_datos_clientes": true
   }
   ```

---

## 🛠️ Desarrollo

### 📋 Comandos Útiles

```bash
# Desarrollo
python manage.py runserver              # Iniciar servidor
python manage.py shell                  # Shell interactivo
python manage.py makemigrations         # Crear migraciones
python manage.py migrate                # Aplicar migraciones

# Testing
python manage.py test                   # Ejecutar tests
python manage.py test apps.core        # Tests específicos

# Datos
python manage.py createsuperuser        # Crear superusuario
python manage.py collectstatic          # Recopilar archivos estáticos
```

### 🔧 Configuración de Desarrollo

**Base de Datos (settings.py):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'arte_ideas_db',
        'USER': 'root',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**JWT Settings:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### 🧪 Testing

**Ejecutar Tests:**
```bash
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test apps.core.tests.test_models
python manage.py test apps.core.tests.test_views
python manage.py test apps.core.tests.test_authentication
```

**Coverage:**
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### 📊 Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| **Modelos** | 8 modelos principales |
| **Endpoints** | 26 endpoints documentados |
| **Roles** | 6 roles con permisos granulares |
| **Módulos** | 10 módulos de negocio |
| **Tests** | Cobertura > 80% |
| **Documentación** | 100% de endpoints documentados |

---

## 📚 Documentación Adicional

### 📁 Archivos de Documentación

- [`API_ENDPOINTS_ARTE_IDEAS.md`](./API_ENDPOINTS_ARTE_IDEAS.md) - Documentación completa de API
- [`docs/`](./docs/) - Documentación técnica detallada
- [`Arte_Ideas_Core_API.postman_collection.json`](./Arte_Ideas_Core_API.postman_collection.json) - Colección Postman
- [`Arte_Ideas_Core_Environment.postman_environment.json`](./Arte_Ideas_Core_Environment.postman_environment.json) - Variables Postman

### 🔗 Enlaces Útiles

- **Health Check:** http://localhost:8000/api/core/health/
- **Django Admin:** http://localhost:8000/admin/
- **API Base:** http://localhost:8000/api/core/

---

## 🤝 Contribución

### 📋 Guías de Contribución

1. **Fork** el repositorio
2. **Crear** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear** un Pull Request

### 🧪 Antes de Contribuir

- ✅ Ejecutar todos los tests
- ✅ Verificar cobertura de código
- ✅ Actualizar documentación
- ✅ Probar endpoints en Postman
- ✅ Verificar multi-tenancy

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👨‍💻 Autor

**Arte Ideas Development Team**

- 📧 Email: dev@arteideas.com
- 🌐 Website: https://arteideas.com
- 📱 GitHub: [@arte-ideas](https://github.com/arte-ideas)

---

## 🙏 Agradecimientos

- Django REST Framework por la excelente API framework
- Simple JWT por la implementación de JWT
- MySQL por la robusta base de datos
- Postman por las herramientas de testing

---

**¡Gracias por usar Arte Ideas Core App! 🎨✨**