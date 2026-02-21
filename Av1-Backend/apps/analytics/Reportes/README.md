# Módulo de Analytics/Reportes - Arte Ideas

## Descripción

Módulo centralizado para la generación y visualización de reportes por área (Ventas, Inventario, Producción, Clientes, Financiero y Contratos).

## Características

### HU06 - Generación y Visualización de Reportes

- ✅ Visualización de reportes clasificados por categoría
- ✅ Métricas de resumen (tarjetas) con datos agregados
- ✅ Tablas de detalle con información completa
- ✅ Filtros por período (fecha_inicio, fecha_fin)
- ✅ Interfaz clara y visual sin necesidad de conocimientos técnicos

### HU08 - Exportación de Reportes

- ✅ Exportación a Excel (.xlsx)
- ✅ Exportación a PDF (.pdf)
- ✅ Incluye encabezados, títulos y formato profesional
- ✅ Nombres de archivo identificables con fecha y hora
- ✅ Exportación del reporte visible (según filtros activos)

## Categorías de Reportes

1. **Ventas**: Reportes de pedidos, ventas totales, pagos, saldos pendientes
2. **Inventario**: Stock disponible, productos bajo stock, valor de inventario
3. **Producción**: Órdenes de producción, tiempos, eficiencia
4. **Clientes**: Clientes por tipo, clientes nuevos, total de pedidos por cliente
5. **Financiero**: Ingresos, pagos recibidos, saldos pendientes, IGV
6. **Contratos**: Contratos activos, montos, adelantos, saldos pendientes

## API Endpoints

### Listar Categorías

```
GET /api/analytics/reportes/categorias/
```

Retorna lista de todas las categorías disponibles.

### Obtener Reporte de una Categoría

```
GET /api/analytics/reportes/{categoria}/
```

Parámetros:
- `categoria`: ventas, inventario, produccion, clientes, financiero, contratos
- `fecha_inicio` (opcional): Fecha inicio en formato YYYY-MM-DD (default: 30 días atrás)
- `fecha_fin` (opcional): Fecha fin en formato YYYY-MM-DD (default: hoy)

Ejemplo:
```
GET /api/analytics/reportes/ventas/?fecha_inicio=2025-01-01&fecha_fin=2025-01-31
```

### Exportar a Excel

```
GET /api/analytics/reportes/{categoria}/exportar/excel/
```

Parámetros:
- `categoria`: ventas, inventario, produccion, clientes, financiero, contratos
- `fecha_inicio` (opcional): Fecha inicio
- `fecha_fin` (opcional): Fecha fin
- `rango` (opcional): visible (default) o completo

Ejemplo:
```
GET /api/analytics/reportes/ventas/exportar/excel/?fecha_inicio=2025-01-01&fecha_fin=2025-01-31
```

### Exportar a PDF

```
GET /api/analytics/reportes/{categoria}/exportar/pdf/
```

Parámetros:
- `categoria`: ventas, inventario, produccion, clientes, financiero, contratos
- `fecha_inicio` (opcional): Fecha inicio
- `fecha_fin` (opcional): Fecha fin
- `rango` (opcional): visible (default) o completo

Ejemplo:
```
GET /api/analytics/reportes/ventas/exportar/pdf/?fecha_inicio=2025-01-01&fecha_fin=2025-01-31
```

### Obtener Todos los Reportes

```
GET /api/analytics/reportes/todos/
```

Retorna resumen de todas las categorías (útil para dashboard).

Parámetros:
- `fecha_inicio` (opcional): Fecha inicio
- `fecha_fin` (opcional): Fecha fin

## Estructura de Respuesta

### Reporte Individual

```json
{
  "categoria": "ventas",
  "titulo": "Reporte de Ventas",
  "periodo_inicio": "2025-01-01",
  "periodo_fin": "2025-01-31",
  "metricas": {
    "total_ventas": 15000.00,
    "total_pedidos": 25,
    "promedio_venta": 600.00,
    "tasa_completitud": 80.0,
    "total_pagado": 12000.00,
    "saldo_pendiente": 3000.00
  },
  "detalle": [
    {
      "id": 1,
      "numero_pedido": "PED-001",
      "cliente": "Juan Pérez",
      "fecha": "2025-01-15",
      "tipo_documento": "Nota de Venta",
      "total": 600.00,
      "pagado": 600.00,
      "saldo": 0.00,
      "estado": "Completado",
      "estado_pago": "Pagado Completo"
    }
  ],
  "fecha_generacion": "2025-01-31T10:30:00Z"
}
```

## Métricas por Categoría

### Ventas
- Total de ventas
- Total de pedidos
- Promedio de venta
- Tasa de completitud
- Total pagado
- Saldo pendiente

### Inventario
- Total de productos
- Total de stock
- Valor total de inventario
- Productos bajo stock
- Productos con stock OK

### Producción
- Total de órdenes
- Órdenes completadas
- Órdenes en proceso
- Órdenes pendientes
- Órdenes vencidas
- Tiempo promedio (horas)
- Tasa de completitud

### Clientes
- Total de clientes
- Clientes particulares
- Clientes colegios
- Clientes empresas
- Clientes nuevos

### Financiero
- Total de ingresos
- Total pagado
- Total de pagos recibidos
- Saldo pendiente
- IGV recaudado
- Ingresos netos

### Contratos
- Total de contratos
- Total de monto
- Total de adelantos
- Total de saldo pendiente
- Contratos activos
- Contratos completados

## Instalación de Dependencias

```bash
pip install -r requirements.txt
```

Las siguientes librerías son necesarias:
- `openpyxl>=3.1.0` - Para exportación a Excel
- `reportlab>=4.0.0` - Para exportación a PDF

## Autenticación

Todas las rutas requieren autenticación JWT. El tenant se obtiene automáticamente del usuario autenticado.

## Notas Técnicas

- Los reportes se filtran automáticamente por tenant del usuario
- Los superusuarios pueden ver todos los datos (si no tienen tenant asignado)
- Las fechas se interpretan en la zona horaria configurada en Django
- Los archivos exportados incluyen fecha y hora en el nombre para evitar sobrescritura

## Ejemplos de Uso

### Obtener Reporte de Ventas del Mes Actual

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
}

response = requests.get(
    'http://localhost:8000/api/analytics/reportes/ventas/',
    headers=headers,
    params={
        'fecha_inicio': '2025-01-01',
        'fecha_fin': '2025-01-31'
    }
)

data = response.json()
print(f"Total de ventas: {data['metricas']['total_ventas']}")
```

### Exportar Reporte a Excel

```python
response = requests.get(
    'http://localhost:8000/api/analytics/reportes/ventas/exportar/excel/',
    headers=headers,
    params={
        'fecha_inicio': '2025-01-01',
        'fecha_fin': '2025-01-31'
    }
)

with open('reporte_ventas.xlsx', 'wb') as f:
    f.write(response.content)
```

## Mantenimiento

Para agregar una nueva categoría de reporte:

1. Crear un nuevo servicio en `services.py` heredando de `ReportService`
2. Implementar métodos `get_metrics()` y `get_detalle()`
3. Agregar la categoría al diccionario `CATEGORIAS` en `views.py`

## Troubleshooting

### Error: "Se requiere openpyxl para exportar a Excel"
- Instalar: `pip install openpyxl`

### Error: "Se requiere reportlab para exportar a PDF"
- Instalar: `pip install reportlab`

### Error: "Usuario no tiene tenant asignado"
- Verificar que el usuario tenga un tenant asignado en la base de datos
- Los superusuarios pueden no tener tenant, pero esto debe manejarse según la lógica de negocio

