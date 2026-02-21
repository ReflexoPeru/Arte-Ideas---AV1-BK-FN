# ⚙️ Especificaciones Técnicas - Arte Ideas (Estudio Fotográfico)

## 🎯 Stack Tecnológico Completo

### Backend Framework
```python
# Core Framework
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1

# Authentication & Security
djangorestframework-simplejwt==5.3.0
django-oauth-toolkit==1.7.1
cryptography==41.0.7

# Database
psycopg2-binary==2.9.9  # PostgreSQL
django-extensions==3.2.3

# Multi-tenancy
django-tenant-schemas==1.10.0  # Alternative approach
django-tenants==3.5.0

# API Documentation
drf-spectacular==0.26.5
django-silk==5.0.4  # Performance profiling
```

### Exportación y Reportes
```python
# PDF Generation
weasyprint==60.2
reportlab==4.0.4
xhtml2pdf==0.2.11

# Excel Generation
openpyxl==3.1.2
xlsxwriter==3.1.9
pandas==2.1.3

# Template Engine
jinja2==3.1.2
```

### Performance y Caching
```python
# Caching
redis==5.0.1
django-redis==5.4.0
django-cachalot==2.6.1  # ORM caching

# Background Tasks
celery==5.3.4
django-celery-beat==2.5.0
django-celery-results==2.5.1

# Monitoring
django-debug-toolbar==4.2.0
sentry-sdk==1.38.0
```

### Storage y Media
```python
# File Storage
django-storages==1.14.2
boto3==1.34.0  # AWS S3
Pillow==10.1.0  # Image processing

# File Validation
python-magic==0.4.27
django-cleanup==8.0.0  # Auto cleanup files
```

## 🏗️ Arquitectura del Sistema

### Estructura de Proyecto
```
arte_ideas_backend/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/
│   ├── crm/
│   ├── commerce/
│   ├── operations/
│   ├── finance/
│   └── analytics/
├── shared/
│   ├── mixins/
│   ├── permissions/
│   ├── serializers/
│   ├── validators/
│   └── utils/
├── templates/
│   └── exports/
├── static/
├── media/
├── tests/
├── docs/
├── requirements/
├── docker/
├── scripts/
└── manage.py
```

### Configuración por Entornos

#### Base Settings
```python
# config/settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = []

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.core',
    'apps.crm',
    'apps.commerce',
    'apps.operations',
    'apps.finance',
    'apps.analytics',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.TenantMiddleware',  # Custom tenant middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'arte_ideas'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'apps.core.permissions.TenantPermission',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Export Settings
EXPORT_SETTINGS = {
    'PDF': {
        'ENGINE': 'weasyprint',
        'TEMPLATE_DIR': 'exports/templates/pdf/',
        'STATIC_URL': '/static/',
        'MAX_FILE_SIZE_MB': 50,
    },
    'EXCEL': {
        'ENGINE': 'openpyxl',
        'MAX_ROWS': 100000,
        'MAX_FILE_SIZE_MB': 25,
    },
    'CSV': {
        'ENCODING': 'utf-8',
        'DELIMITER': ',',
        'MAX_ROWS': 500000,
    },
    'STORAGE': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'LOCATION': 'media/exports/',
        'RETENTION_DAYS': 7,
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

#### Development Settings
```python
# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

#### Production Settings
```python
# config/settings/production.py
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# CORS for production
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Sentry for error tracking
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,
    send_default_pii=True,
)

# File Storage (AWS S3)
if os.environ.get('USE_S3') == 'True':
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

## 🐳 Containerización con Docker

### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        libfreetype6-dev \
        zlib1g-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: arte_ideas
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=1
      - DB_HOST=db
      - DB_NAME=arte_ideas
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - REDIS_URL=redis://redis:6379/0

  celery:
    build: .
    command: celery -A config worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=1
      - DB_HOST=db
      - DB_NAME=arte_ideas
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - REDIS_URL=redis://redis:6379/0

  celery-beat:
    build: .
    command: celery -A config beat -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=1
      - DB_HOST=db
      - DB_NAME=arte_ideas
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - REDIS_URL=redis://redis:6379/0

volumes:
  postgres_data:
```

## 🔒 Configuración de Seguridad

### Variables de Entorno
```bash
# .env.example
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=arte_ideas
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# AWS S3 (optional)
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Sentry (optional)
SENTRY_DSN=your-sentry-dsn

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Roles y Permisos del Sistema
```python
# apps/core/constants.py
SYSTEM_ROLES = {
    'ADMIN': {
        'name': 'Administrador',
        'permissions': {
            'core': ['view', 'add', 'change', 'delete'],
            'crm': ['view', 'add', 'change', 'delete'],
            'commerce': ['view', 'add', 'change', 'delete'],
            'operations': ['view', 'add', 'change', 'delete'],
            'finance': ['view', 'add', 'change', 'delete'],
            'analytics': ['view', 'add', 'change', 'delete'],
        }
    },
    'SALES': {
        'name': 'Ventas',
        'permissions': {
            'core': ['view'],
            'crm': ['view', 'add', 'change'],
            'commerce': ['view', 'add', 'change'],
            'operations': ['view'],
            'finance': ['view'],
            'analytics': ['view'],
        }
    },
    'PRODUCTION': {
        'name': 'Producción',
        'permissions': {
            'core': ['view'],
            'crm': ['view'],
            'commerce': ['view'],
            'operations': ['view', 'add', 'change'],
            'finance': ['view'],
            'analytics': ['view'],
        }
    },
    'OPERATOR': {
        'name': 'Operario',
        'permissions': {
            'core': ['view'],
            'crm': ['view'],
            'commerce': ['view'],
            'operations': ['view', 'change'],
            'finance': ['view', 'add'],
            'analytics': ['view'],
        }
    }
}

MODULE_PERMISSIONS = {
    'dashboard': ['view'],
    'profile': ['view', 'change'],
    'configuration': ['view', 'change'],
    'clients': ['view', 'add', 'change', 'delete'],
    'appointments': ['view', 'add', 'change', 'delete'],
    'contracts': ['view', 'add', 'change', 'delete'],
    'orders': ['view', 'add', 'change', 'delete'],
    'inventory': ['view', 'add', 'change', 'delete'],
    'assets': ['view', 'add', 'change', 'delete'],
    'production': ['view', 'add', 'change', 'delete'],
    'expenses': ['view', 'add', 'change', 'delete'],
    'reports': ['view', 'add', 'change', 'delete'],
}
```

## 📊 Performance y Monitoreo

### Configuración de Monitoring
```python
# apps/core/monitoring.py
import time
import logging
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        queries_before = len(connection.queries)
        
        response = self.get_response(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        queries_count = len(connection.queries) - queries_before
        
        # Log slow requests
        if duration > 1.0:  # Log requests slower than 1 second
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"took {duration:.2f}s with {queries_count} queries"
            )
        
        # Add headers for debugging
        if settings.DEBUG:
            response['X-Response-Time'] = f"{duration:.3f}s"
            response['X-DB-Queries'] = str(queries_count)
        
        return response
```

### Health Check Endpoints
```python
# apps/core/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
import redis

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for load balancers"""
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check Redis
    try:
        cache.set('health_check', 'ok', 30)
        cache.get('health_check')
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code)
```

## 🧪 Testing Configuration

### Test Settings
```python
# config/settings/testing.py
from .base import *

# Use in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use dummy cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging during tests
LOGGING_CONFIG = None

# Password hashers (faster for tests)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
```

## 📋 Checklist de Configuración

### ✅ Configuración Base
- [ ] Django y DRF instalados
- [ ] Configuración multi-entorno (dev/prod/test)
- [ ] Base de datos PostgreSQL configurada
- [ ] Redis para cache y Celery configurado

### ✅ Autenticación y Seguridad
- [ ] JWT authentication implementado
- [ ] Sistema de roles y permisos configurado
- [ ] Middleware de seguridad habilitado
- [ ] Variables de entorno configuradas

### ✅ Multi-tenancy
- [ ] Tenant middleware implementado
- [ ] Modelos base con tenant_id
- [ ] Managers con filtros automáticos
- [ ] Permisos multi-tenant configurados

### ✅ Performance
- [ ] Cache Redis configurado
- [ ] Celery para tareas asíncronas
- [ ] Índices de base de datos optimizados
- [ ] Monitoring y logging configurado

### ✅ Deployment
- [ ] Docker y docker-compose configurados
- [ ] Configuración de producción lista
- [ ] Health checks implementados
- [ ] CI/CD pipeline configurado

---
*Especificaciones técnicas completas para un sistema robusto y escalable*