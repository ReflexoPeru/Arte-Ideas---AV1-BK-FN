# MÓDULO: INVENTARIO

## 1. Descripción General

El Módulo de Inventario es el encargado de la gestión y control de materiales, molduras y recursos utilizados en los procesos de enmarcado, producción y venta.

**Su objetivo principal es:**
- Registrar y mantener actualizado el stock
- Controlar los costos unitarios y totales
- Garantizar la disponibilidad de insumos para la producción
- Evitar faltantes mediante alertas de stock mínimo

## 2. Estructura del Módulo

### Modelos Implementados

#### CATEGORÍA: ENMARCADOS
- **MolduraListon**: Molduras (Listones) con especificaciones de ancho, color y material
- **MolduraPrearmada**: Molduras ya preparadas con dimensiones específicas
- **VidrioTapaMDF**: Vidrios y tapas MDF con diferentes grosores y tamaños
- **Paspartu**: Láminas para acabados personalizados

#### CATEGORÍA: MINILAB
- **Minilab**: Insumos para impresión (papeles, químicos, reveladores)

#### CATEGORÍA: GRADUACIONES
- **Cuadro**: Productos finales para graduaciones (canvas, papel fotográfico)
- **Anuario**: Anuarios con diferentes formatos y tipos de tapa

#### CATEGORÍA: CORTE LÁSER
- **CorteLaser**: Materiales para servicios de corte láser (MDF, acrílico, etc.)

#### CATEGORÍA: ACCESORIOS
- **MarcoAccesorio**: Ganchos, soportes y accesorios para marcos
- **HerramientaGeneral**: Herramientas de trabajo (cortadores, reglas, etc.)

## 3. Funcionalidades Principales

### API REST Completa
- **CRUD completo** para todos los modelos de inventario
- **Endpoints específicos** para métricas y alertas
- **Filtros y búsquedas** avanzadas
- **Autenticación** requerida para todas las operaciones

### Sistema de Alertas
- Alertas automáticas cuando el stock llega al nivel mínimo configurado
- Endpoints específicos para productos con alertas de stock
- API para productos con stock crítico (bajo 20% del mínimo)

### Cálculos Automáticos
- **Costo Total**: Calculado automáticamente (costo_unitario × stock_disponible)
- **Estado de Alerta**: Verificación automática del nivel de stock

## 4. API Endpoints

### Endpoints Principales
- `GET /api/dashboard/`: Métricas principales del inventario
- `GET /api/metricas/`: Métricas detalladas por categoría

### Endpoints por Categoría (CRUD completo)
- `/api/moldura-liston/`: Molduras (Listones)
- `/api/moldura-prearmada/`: Molduras Prearmadas
- `/api/vidrio-tapa-mdf/`: Vidrios y Tapas MDF
- `/api/paspartu/`: Paspartús
- `/api/minilab/`: Insumos Minilab
- `/api/cuadro/`: Cuadros
- `/api/anuario/`: Anuarios
- `/api/corte-laser/`: Materiales Corte Láser
- `/api/marco-accesorio/`: Marcos y Accesorios
- `/api/herramienta-general/`: Herramientas Generales

### Endpoints Especiales
- `GET /{categoria}/alertas_stock/`: Productos con alertas de stock por categoría
- `GET /{categoria}/bajo_stock/`: Productos con stock crítico por categoría

### Administración Django
Todos los modelos están registrados en el admin de Django con interfaces personalizadas que incluyen:
- Filtros por categoría, material, color, etc.
- Búsqueda por nombre de producto
- Visualización de alertas de stock
- Campos calculados (costo total, estado de alerta)


## 5. Instalación y Configuración

1. **Agregar a INSTALLED_APPS** en settings.py:
```python
INSTALLED_APPS = [
    # ... otras apps
    'apps.commerce.inventario',
]
```

2. **Ejecutar migraciones**:
```bash
python manage.py makemigrations inventario
python manage.py migrate
```

3. **Crear superusuario** (si no existe):
```bash
python manage.py createsuperuser
```

4. **Acceder al admin** en `/admin/` para comenzar a cargar productos

## 6. Relación con Otros Módulos

| Módulo | Relación con Inventario |
|--------|------------------------|
| **Pedidos** | Descarga de stock al registrar ventas |
| **Activas** | Actualiza stock al consumir repuestos/insumos |
| **Gastos** | Sincronización de costos de adquisición |
| **Producción** | Control de materiales en órdenes de trabajo |
| **Reportes** | Informes de stock, costos y alertas |

## 7. Beneficios del Módulo

- ✅ Optimización en la gestión de insumos
- ✅ Control detallado de costos unitarios y totales
- ✅ Prevención de faltantes con sistema de stock mínimo
- ✅ Trazabilidad completa por línea de negocio
- ✅ API REST completa con autenticación
- ✅ Interface administrativa intuitiva
- ✅ Sistema de alertas automático
- ✅ Endpoints especializados para análisis de stock