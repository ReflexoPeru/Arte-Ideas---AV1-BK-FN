# Core App - Arte Ideas

## Estructura Reorganizada (Arquitectura Modular)

La carpeta `core/` ha sido reorganizada siguiendo las buenas prácticas de Django y un patrón de arquitectura modular para mejorar la mantenibilidad y escalabilidad del sistema.

### 📁 Estructura de Carpetas

```
apps/core/
├── autenticacion/          # Módulo de Autenticación
│   ├── __init__.py
│   ├── models.py          # User, RolePermission
│   ├── views.py           # LogoutView
│   ├── serializers.py     # LogoutSerializer
│   ├── urls.py            # URLs de autenticación
│   ├── admin.py           # Admin para usuarios y permisos
│   ├── signals.py         # Signals de autenticación
│   └── tests.py           # Tests del módulo
│
├── usuarios/               # Módulo de Usuarios
│   ├── __init__.py
│   ├── models.py          # UserProfile, UserActivity
│   ├── views.py           # ProfileView, ChangePasswordView, etc.
│   ├── serializers.py     # UserSerializer, ChangePasswordSerializer, etc.
│   ├── urls.py            # URLs de perfiles y usuarios
│   ├── admin.py           # Admin para perfiles y actividades
│   ├── signals.py         # Signals para creación de perfiles
│   └── tests.py           # Tests del módulo
│
├── configuracion_sistema/  # Módulo de Configuración del Sistema
│   ├── __init__.py
│   ├── models.py          # SystemConfiguration
│   ├── views.py           # BusinessConfigurationView, UsersManagementView, etc.
│   ├── serializers.py     # TenantSerializer, UserManagementSerializer, etc.
│   ├── urls.py            # URLs de configuración y administración
│   ├── admin.py           # Admin para configuraciones
│   └── tests.py           # Tests del módulo
│
├── multitenancy/          # Módulo de Multi-tenancy
│   ├── __init__.py
│   ├── models.py          # Tenant, TenantConfiguration
│   ├── middleware.py      # TenantMiddleware, TenantValidationMiddleware
│   ├── admin.py           # Admin para tenants
│   └── tests.py           # Tests del módulo
│
├── migrations/            # Migraciones de Django
├── __init__.py
├── models.py             # Importaciones para compatibilidad
├── views.py              # Vista de health check
├── urls.py               # URLs principales reorganizadas
├── admin.py              # Importaciones centralizadas de admins
├── apps.py               # Configuración de la app con signals
├── tests.py              # Tests generales
└── README.md             # Esta documentación
```

### 🎯 Responsabilidades por Módulo

#### 1. **autenticacion/** - Autenticación y Permisos
- **Propósito**: Gestión de login, logout, registro, roles y permisos
- **Modelos**: `User`, `RolePermission`
- **Funcionalidades**:
  - Autenticación de usuarios
  - Gestión de roles (super_admin, admin, ventas, produccion, operario)
  - Sistema de permisos granular por módulos y acciones
  - Logout con invalidación de tokens JWT

#### 2. **usuarios/** - Gestión de Usuarios
- **Propósito**: Perfiles de usuario, actividades y gestión personal
- **Modelos**: `UserProfile`, `UserActivity`
- **Funcionalidades**:
  - Perfiles extendidos de usuario (preferencias, configuraciones)
  - Registro de actividades del usuario
  - Cambio de contraseña y email
  - Estadísticas personales del usuario

#### 3. **configuracion_sistema/** - Administración del Sistema
- **Propósito**: Configuraciones generales, administración de usuarios y negocio
- **Modelos**: `SystemConfiguration`
- **Funcionalidades**:
  - Configuración del negocio (datos de la empresa)
  - Gestión de usuarios del tenant (crear, editar, eliminar)
  - Gestión de roles y permisos
  - Administración de tenants (solo super admin)

#### 4. **multitenancy/** - Multi-tenancy
- **Propósito**: Gestión de tenants y configuraciones específicas
- **Modelos**: `Tenant`, `TenantConfiguration`
- **Funcionalidades**:
  - Gestión de estudios fotográficos (tenants)
  - Configuraciones específicas por tenant
  - Middleware para identificación de tenant
  - Restricciones por ubicación (Lima vs Provincia)

### 🔗 URLs Reorganizadas

```python
# apps/core/urls.py
urlpatterns = [
    path('health/', CoreHealthCheckView.as_view(), name='health_check'),
    path('auth/', include('apps.core.autenticacion.urls')),           # /api/core/auth/
    path('users/', include('apps.core.usuarios.urls')),              # /api/core/users/
    path('config/', include('apps.core.configuracion_sistema.urls')), # /api/core/config/
]
```

### 🔄 Compatibilidad con Migraciones

El archivo `models.py` principal mantiene las importaciones de todos los modelos para asegurar compatibilidad con las migraciones existentes de Django:

```python
# Importar todos los modelos desde los nuevos módulos
from .autenticacion.models import User, RolePermission
from .usuarios.models import UserProfile, UserActivity
from .configuracion_sistema.models import SystemConfiguration
from .multitenancy.models import Tenant, TenantConfiguration
```

### 🧪 Testing

Cada módulo tiene su propio archivo `tests.py` con tests específicos para sus funcionalidades:

- `autenticacion/tests.py` - Tests de autenticación y permisos
- `usuarios/tests.py` - Tests de perfiles y actividades
- `configuracion_sistema/tests.py` - Tests de configuraciones
- `multitenancy/tests.py` - Tests de tenants y multi-tenancy

### 📊 Admin Interface

Los admins están organizados por módulo pero se importan centralizadamente en `admin.py`:

- Filtros automáticos por tenant según permisos del usuario
- Permisos granulares según rol (super_admin, admin, etc.)
- Interfaces específicas para cada tipo de modelo

### 🔧 Signals

Los signals están organizados por módulo:

- `autenticacion/signals.py` - Creación automática de permisos por rol
- `usuarios/signals.py` - Creación automática de perfiles de usuario

### 🚀 Beneficios de la Nueva Estructura

1. **Separación Clara de Responsabilidades**: Cada módulo tiene un propósito específico
2. **Mantenibilidad**: Código más fácil de mantener y debuggear
3. **Escalabilidad**: Fácil agregar nuevos módulos sin afectar existentes
4. **Testing**: Tests organizados por funcionalidad
5. **Compatibilidad**: Mantiene compatibilidad con código existente
6. **Multi-tenancy**: Soporte robusto para múltiples estudios fotográficos

### 🔄 Migración Gradual

La estructura permite migración gradual:
1. ✅ Modelos reorganizados con importaciones de compatibilidad
2. ✅ URLs actualizadas con nueva estructura
3. ✅ Admin reorganizado con importaciones centralizadas
4. ✅ Tests creados para cada módulo
5. 🔄 Próximo: Migrar vistas existentes de otras apps para usar nueva estructura

### 📝 Notas Importantes

- **Multi-tenancy**: El sistema mantiene compatibilidad completa con multi-tenancy
- **Permisos**: Sistema de permisos granular por rol y tenant
- **Middleware**: Incluye middleware para identificación automática de tenant
- **Signals**: Creación automática de perfiles y permisos
- **Admin**: Filtros automáticos según permisos del usuario logueado

Esta reorganización establece una base sólida para el crecimiento futuro del sistema manteniendo la funcionalidad existente.