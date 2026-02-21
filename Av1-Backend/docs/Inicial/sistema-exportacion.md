# 📊 Sistema de Exportación - Arte Ideas

## 🎯 Estrategia de Exportación Multi-Formato

**Arte Ideas** implementa un sistema modular de exportación que permite generar reportes en **PDF**, **Excel** y **CSV** según las necesidades de cada módulo y rol de usuario.

## 📋 Matriz de Exportación por Módulo

| Módulo Frontend | App Backend | PDF | Excel | CSV | Casos de Uso |
|----------------|-------------|-----|-------|-----|--------------|
| **Mi Perfil** | Core | ❌ | ❌ | ❌ | No requiere exportación |
| **Configuración** | Core | ❌ | ❌ | ✅ | Backup configuraciones |
| **Clientes** | CRM | ✅ | ✅ | ✅ | Listados, fichas, mailing |
| **Agenda** | CRM | ✅ | ✅ | ❌ | Programación, reportes |
| **Contratos** | CRM | ✅ | ❌ | ❌ | Documentos legales |
| **Pedidos** | Commerce | ✅ | ✅ | ✅ | Facturas, análisis ventas |
| **Inventario** | Commerce | ❌ | ✅ | ✅ | Control stock, valorización |
| **Activos** | Operations | ❌ | ✅ | ✅ | Inventario, depreciación |
| **Producción** | Operations | ✅ | ✅ | ❌ | Órdenes, reportes |
| **Gastos** | Finance | ✅ | ✅ | ✅ | Comprobantes, análisis |
| **Dashboard** | Analytics | ✅ | ❌ | ❌ | Reportes ejecutivos |
| **Reportes** | Analytics | ✅ | ✅ | ✅ | Todos los formatos |

## 🛠️ Stack Tecnológico de Exportación

### Librerías Principales
```python
# requirements.txt
# PDF Generation
weasyprint==60.2
reportlab==4.0.4

# Excel Generation
openpyxl==3.1.2
xlsxwriter==3.1.9

# CSV Generation (built-in)
# csv (Python standard library)

# Template Engine
jinja2==3.1.2

# Image Processing (for PDFs)
Pillow==10.0.1
```

### Configuración Base
```python
# settings.py
EXPORT_SETTINGS = {
    'PDF': {
        'ENGINE': 'weasyprint',  # or 'reportlab'
        'TEMPLATE_DIR': 'exports/templates/pdf/',
        'STATIC_URL': '/static/',
        'MAX_FILE_SIZE_MB': 50,
    },
    'EXCEL': {
        'ENGINE': 'openpyxl',  # or 'xlsxwriter'
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
        'RETENTION_DAYS': 7,  # Auto-delete after 7 days
    }
}
```

## 🏗️ Arquitectura del Sistema

### Base Export Service
```python
# core/services/export_service.py
from abc import ABC, abstractmethod
from django.conf import settings
from django.core.files.storage import default_storage
import uuid
from datetime import datetime, timedelta

class BaseExportService(ABC):
    def __init__(self, tenant, user, export_type):
        self.tenant = tenant
        self.user = user
        self.export_type = export_type.upper()
        self.settings = settings.EXPORT_SETTINGS[self.export_type]
        
    @abstractmethod
    def generate(self, data, template_name, context=None):
        """Generar archivo de exportación"""
        pass
        
    def get_filename(self, base_name):
        """Generar nombre único de archivo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = self.get_file_extension()
        return f"{base_name}_{timestamp}_{unique_id}.{extension}"
        
    @abstractmethod
    def get_file_extension(self):
        """Obtener extensión del archivo"""
        pass
        
    def save_file(self, content, filename):
        """Guardar archivo en storage"""
        file_path = f"exports/{self.tenant.id}/{filename}"
        return default_storage.save(file_path, content)
        
    def cleanup_old_files(self):
        """Limpiar archivos antiguos"""
        retention_days = self.settings.get('RETENTION_DAYS', 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Implementar limpieza según storage backend
        pass
```

### PDF Export Service
```python
# core/services/pdf_export_service.py
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
import base64

class PDFExportService(BaseExportService):
    def __init__(self, tenant, user):
        super().__init__(tenant, user, 'PDF')
        
    def generate(self, data, template_name, context=None):
        """Generar PDF usando WeasyPrint"""
        if context is None:
            context = {}
            
        # Agregar datos del tenant y configuración
        context.update({
            'tenant': self.tenant,
            'user': self.user,
            'data': data,
            'generated_at': datetime.now(),
            'static_url': self.settings['STATIC_URL'],
        })
        
        # Renderizar template HTML
        html_content = render_to_string(
            f"{self.settings['TEMPLATE_DIR']}{template_name}.html",
            context
        )
        
        # Generar PDF
        html = HTML(string=html_content, base_url=self.settings['STATIC_URL'])
        pdf_file = html.write_pdf()
        
        return BytesIO(pdf_file)
        
    def get_file_extension(self):
        return 'pdf'
        
    def generate_invoice(self, order):
        """Generar factura PDF"""
        context = {
            'order': order,
            'items': order.items.all(),
            'client': order.client,
            'total': order.total,
        }
        
        pdf_content = self.generate(
            data=order,
            template_name='invoice',
            context=context
        )
        
        filename = self.get_filename(f"factura_{order.order_number}")
        file_path = self.save_file(pdf_content, filename)
        
        return file_path
        
    def generate_contract(self, contract):
        """Generar contrato PDF"""
        context = {
            'contract': contract,
            'client': contract.client,
            'terms': contract.get_terms(),
        }
        
        pdf_content = self.generate(
            data=contract,
            template_name='contract',
            context=context
        )
        
        filename = self.get_filename(f"contrato_{contract.id}")
        file_path = self.save_file(pdf_content, filename)
        
        return file_path
```

### Excel Export Service
```python
# core/services/excel_export_service.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
from io import BytesIO

class ExcelExportService(BaseExportService):
    def __init__(self, tenant, user):
        super().__init__(tenant, user, 'EXCEL')
        
    def generate(self, data, template_name, context=None):
        """Generar Excel usando openpyxl"""
        wb = Workbook()
        ws = wb.active
        
        # Configurar estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Generar contenido según template
        if template_name == 'clients_list':
            self._generate_clients_excel(ws, data, header_font, header_fill)
        elif template_name == 'orders_report':
            self._generate_orders_excel(ws, data, header_font, header_fill)
        elif template_name == 'inventory_report':
            self._generate_inventory_excel(ws, data, header_font, header_fill)
        elif template_name == 'expenses_report':
            self._generate_expenses_excel(ws, data, header_font, header_fill)
            
        # Guardar en BytesIO
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        return excel_file
        
    def get_file_extension(self):
        return 'xlsx'
        
    def _generate_clients_excel(self, ws, clients, header_font, header_fill):
        """Generar reporte de clientes"""
        ws.title = "Clientes"
        
        # Headers
        headers = ['ID', 'Nombre', 'Email', 'Teléfono', 'Tipo', 'Fecha Registro']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            
        # Data
        for row, client in enumerate(clients, 2):
            ws.cell(row=row, column=1, value=client.id)
            ws.cell(row=row, column=2, value=client.name)
            ws.cell(row=row, column=3, value=client.email)
            ws.cell(row=row, column=4, value=client.phone)
            ws.cell(row=row, column=5, value=client.get_client_type_display())
            ws.cell(row=row, column=6, value=client.created_at.strftime('%Y-%m-%d'))
            
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
            
    def _generate_orders_excel(self, ws, orders, header_font, header_fill):
        """Generar reporte de pedidos"""
        ws.title = "Pedidos"
        
        headers = ['Número', 'Cliente', 'Fecha', 'Estado', 'Subtotal', 'Impuestos', 'Total']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            
        for row, order in enumerate(orders, 2):
            ws.cell(row=row, column=1, value=order.order_number)
            ws.cell(row=row, column=2, value=order.client.name)
            ws.cell(row=row, column=3, value=order.order_date.strftime('%Y-%m-%d'))
            ws.cell(row=row, column=4, value=order.get_status_display())
            ws.cell(row=row, column=5, value=float(order.subtotal))
            ws.cell(row=row, column=6, value=float(order.tax))
            ws.cell(row=row, column=7, value=float(order.total))
```

### CSV Export Service
```python
# core/services/csv_export_service.py
import csv
from io import StringIO, BytesIO

class CSVExportService(BaseExportService):
    def __init__(self, tenant, user):
        super().__init__(tenant, user, 'CSV')
        
    def generate(self, data, template_name, context=None):
        """Generar CSV"""
        output = StringIO()
        
        if template_name == 'clients_list':
            self._generate_clients_csv(output, data)
        elif template_name == 'orders_report':
            self._generate_orders_csv(output, data)
        elif template_name == 'inventory_report':
            self._generate_inventory_csv(output, data)
        elif template_name == 'expenses_report':
            self._generate_expenses_csv(output, data)
            
        # Convertir a BytesIO
        csv_content = output.getvalue()
        output.close()
        
        csv_file = BytesIO(csv_content.encode(self.settings['ENCODING']))
        return csv_file
        
    def get_file_extension(self):
        return 'csv'
        
    def _generate_clients_csv(self, output, clients):
        """Generar CSV de clientes"""
        writer = csv.writer(output, delimiter=self.settings['DELIMITER'])
        
        # Headers
        writer.writerow(['ID', 'Nombre', 'Email', 'Teléfono', 'Tipo', 'Fecha Registro'])
        
        # Data
        for client in clients:
            writer.writerow([
                client.id,
                client.name,
                client.email,
                client.phone,
                client.get_client_type_display(),
                client.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
```

## 🎨 Templates de Exportación

### Template PDF - Factura
```html
<!-- exports/templates/pdf/invoice.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Factura {{ order.order_number }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.4;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #366092;
            padding-bottom: 20px;
        }
        
        .company-info {
            float: left;
            width: 50%;
        }
        
        .invoice-info {
            float: right;
            width: 50%;
            text-align: right;
        }
        
        .client-info {
            clear: both;
            margin: 30px 0;
            padding: 15px;
            background-color: #f5f5f5;
        }
        
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .items-table th,
        .items-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        .items-table th {
            background-color: #366092;
            color: white;
        }
        
        .totals {
            float: right;
            width: 300px;
            margin-top: 20px;
        }
        
        .total-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        
        .total-final {
            font-weight: bold;
            font-size: 16px;
            border-top: 2px solid #366092;
            padding-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ tenant.name }}</h1>
        <h2>FACTURA</h2>
    </div>
    
    <div class="company-info">
        <h3>Información de la Empresa</h3>
        <p>{{ tenant.name }}</p>
        <p>{{ tenant.address|default:"" }}</p>
        <p>{{ tenant.phone|default:"" }}</p>
    </div>
    
    <div class="invoice-info">
        <h3>Factura #{{ order.order_number }}</h3>
        <p><strong>Fecha:</strong> {{ order.order_date|date:"d/m/Y" }}</p>
        <p><strong>Estado:</strong> {{ order.get_status_display }}</p>
        {% if order.delivery_date %}
        <p><strong>Entrega:</strong> {{ order.delivery_date|date:"d/m/Y" }}</p>
        {% endif %}
    </div>
    
    <div class="client-info">
        <h3>Información del Cliente</h3>
        <p><strong>{{ client.name }}</strong></p>
        <p>{{ client.email }}</p>
        <p>{{ client.phone }}</p>
        {% if client.address %}
        <p>{{ client.address }}</p>
        {% endif %}
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Precio Unitario</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ item.product.name }}</td>
                <td>{{ item.quantity }}</td>
                <td>${{ item.unit_price|floatformat:2 }}</td>
                <td>${{ item.total_price|floatformat:2 }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="totals">
        <div class="total-row">
            <span>Subtotal:</span>
            <span>${{ order.subtotal|floatformat:2 }}</span>
        </div>
        <div class="total-row">
            <span>Impuestos:</span>
            <span>${{ order.tax|floatformat:2 }}</span>
        </div>
        <div class="total-row total-final">
            <span>TOTAL:</span>
            <span>${{ order.total|floatformat:2 }}</span>
        </div>
    </div>
    
    <div style="clear: both; margin-top: 50px; text-align: center; font-size: 10px; color: #666;">
        <p>Generado el {{ generated_at|date:"d/m/Y H:i" }} por {{ user.get_full_name }}</p>
    </div>
</body>
</html>
```

## 🔗 Integración con ViewSets

### Mixin para Exportación
```python
# core/mixins.py
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .services.pdf_export_service import PDFExportService
from .services.excel_export_service import ExcelExportService
from .services.csv_export_service import CSVExportService

class ExportMixin:
    export_formats = ['pdf', 'excel', 'csv']
    export_template_name = None
    
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Endpoint genérico de exportación"""
        export_format = request.data.get('format', 'pdf').lower()
        
        if export_format not in self.export_formats:
            return Response(
                {'error': f'Formato no soportado. Use: {", ".join(self.export_formats)}'},
                status=400
            )
            
        # Obtener datos para exportar
        queryset = self.filter_queryset(self.get_queryset())
        
        # Aplicar filtros adicionales si se proporcionan
        filters = request.data.get('filters', {})
        if filters:
            queryset = queryset.filter(**filters)
            
        # Generar exportación
        service = self.get_export_service(export_format)
        template_name = self.export_template_name or self.get_export_template_name()
        
        try:
            file_content = service.generate(
                data=queryset,
                template_name=template_name,
                context=request.data.get('context', {})
            )
            
            filename = service.get_filename(self.get_export_filename())
            
            # Retornar archivo
            response = HttpResponse(
                file_content.getvalue(),
                content_type=self.get_content_type(export_format)
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error generando exportación: {str(e)}'},
                status=500
            )
            
    def get_export_service(self, format_type):
        """Obtener servicio de exportación según formato"""
        services = {
            'pdf': PDFExportService,
            'excel': ExcelExportService,
            'csv': CSVExportService,
        }
        
        service_class = services.get(format_type)
        return service_class(self.request.tenant, self.request.user)
        
    def get_export_template_name(self):
        """Obtener nombre del template por defecto"""
        return f"{self.basename}_list"
        
    def get_export_filename(self):
        """Obtener nombre base del archivo"""
        return f"{self.basename}_export"
        
    def get_content_type(self, format_type):
        """Obtener content type según formato"""
        content_types = {
            'pdf': 'application/pdf',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv',
        }
        return content_types.get(format_type, 'application/octet-stream')
```

### Implementación en ViewSets
```python
# crm/views.py
from core.mixins import ExportMixin

class ClientViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    export_formats = ['pdf', 'excel', 'csv']
    export_template_name = 'clients_list'
    
    def get_export_filename(self):
        return 'clientes_export'

# commerce/views.py
class OrderViewSet(ExportMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    export_formats = ['pdf', 'excel', 'csv']
    export_template_name = 'orders_report'
    
    @action(detail=True, methods=['get'])
    def invoice_pdf(self, request, pk=None):
        """Generar factura PDF específica"""
        order = self.get_object()
        service = PDFExportService(request.tenant, request.user)
        
        file_path = service.generate_invoice(order)
        
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(
                pdf_file.read(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="factura_{order.order_number}.pdf"'
            return response
```

## 📊 Monitoreo y Límites

### Tracking de Exportaciones
```python
# analytics/models.py
class ExportLog(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    export_type = models.CharField(max_length=20)
    format = models.CharField(max_length=10)
    template_name = models.CharField(max_length=50)
    records_count = models.IntegerField()
    file_size_mb = models.DecimalField(max_digits=8, decimal_places=2)
    generation_time_seconds = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
```

### Límites y Validaciones
```python
# core/validators.py
class ExportValidator:
    @staticmethod
    def validate_export_limits(tenant, user, queryset, format_type):
        """Validar límites de exportación"""
        settings_key = format_type.upper()
        max_rows = settings.EXPORT_SETTINGS[settings_key].get('MAX_ROWS', 10000)
        
        if queryset.count() > max_rows:
            raise ValidationError(
                f'La exportación excede el límite de {max_rows} registros'
            )
            
        # Validar límites por tenant
        daily_exports = ExportLog.objects.filter(
            tenant=tenant,
            created_at__date=timezone.now().date()
        ).count()
        
        max_daily_exports = tenant.settings.get('max_daily_exports', 50)
        if daily_exports >= max_daily_exports:
            raise ValidationError(
                f'Se ha alcanzado el límite diario de {max_daily_exports} exportaciones'
            )
```

## 📋 Checklist de Implementación

### ✅ Setup Base
- [ ] Librerías de exportación instaladas
- [ ] Configuración EXPORT_SETTINGS definida
- [ ] BaseExportService implementado
- [ ] Storage para archivos configurado

### ✅ Servicios de Exportación
- [ ] PDFExportService implementado
- [ ] ExcelExportService implementado
- [ ] CSVExportService implementado
- [ ] Templates PDF creados

### ✅ Integración con APIs
- [ ] ExportMixin implementado
- [ ] ViewSets con exportación configurados
- [ ] Endpoints de exportación funcionando
- [ ] Validaciones de límites implementadas

### ✅ Monitoreo
- [ ] ExportLog modelo creado
- [ ] Tracking de exportaciones implementado
- [ ] Límites por tenant configurados
- [ ] Limpieza automática de archivos

---
*Sistema de exportación modular y escalable para todos los módulos de negocio*