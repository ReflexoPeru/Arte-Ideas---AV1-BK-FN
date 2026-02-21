"""
Modelos de Pedidos - Arte Ideas Commerce
Gestión de pedidos, órdenes y operaciones comerciales
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from apps.core.models import Tenant
from apps.crm.models import Cliente, Contrato


class Order(models.Model):
    """
    Modelo para pedidos del estudio fotográfico
    Soporta diferentes tipos de documentos: Proforma, Nota de Venta, Contrato
    """
    DOCUMENT_TYPE_CHOICES = [
        ('proforma', 'Proforma'),
        ('nota_venta', 'Nota de Venta'),
        ('contrato', 'Contrato'),
    ]
    
    ORDER_STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]
    
    CLIENT_TYPE_CHOICES = [
        ('particular', 'Particular'),
        ('colegio', 'Colegio'),
        ('empresa', 'Empresa'),
    ]
    
    SCHOOL_LEVEL_CHOICES = [
        ('inicial', 'Inicial'),
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('parcial', 'Pago Parcial'),
        ('completo', 'Pagado Completo'),
    ]
    
    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Estudio Fotográfico')
    
    # Información del pedido
    order_number = models.CharField(max_length=50, verbose_name='Número de Pedido')
    
    # Cliente (relación con CRM)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name='Cliente', related_name='pedidos')
    
    # Tipo de documento y cliente
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Tipo de Documento'
    )
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        verbose_name='Tipo de Cliente'
    )
    
    # Campos específicos para colegios y empresas
    school_level = models.CharField(
        max_length=20,
        choices=SCHOOL_LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name='Nivel (Colegios)'
    )
    grade = models.CharField(max_length=50, blank=True, null=True, verbose_name='Grado')
    section = models.CharField(max_length=50, blank=True, null=True, verbose_name='Sección')
    
    # Fechas importantes
    order_date = models.DateField(default=timezone.now, verbose_name='Fecha del Pedido')
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    delivery_date = models.DateField(verbose_name='Fecha de Entrega')
    
    # Fechas programadas (JSON para flexibilidad)
    scheduled_dates = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Fechas Programadas',
        help_text='Contiene sesiones_fotograficas y entregas como listas de objetos con fecha y hora'
    )
    
    # Información de entrega
    delivery_address = models.TextField(blank=True, verbose_name='Dirección de Entrega')
    delivery_notes = models.TextField(blank=True, verbose_name='Notas de Entrega')
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='IGV')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Monto Pagado')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Saldo Pendiente')
    
    # Estado de pago
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pendiente',
        verbose_name='Estado de Pago'
    )
    
    # Servicios extras
    extra_services = models.TextField(blank=True, verbose_name='Servicios Extras')
    
    # Estado del pedido
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    
    # Relación con contrato (cuando el tipo es 'contrato')
    contrato = models.ForeignKey(
        Contrato, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Contrato Relacionado',
        related_name='pedidos'
    )
    
    # Notas e información adicional
    notes = models.TextField(blank=True, verbose_name='Notas')
    description = models.TextField(blank=True, verbose_name='Descripción del Pedido')
    
    # Control de inventario
    affects_inventory = models.BooleanField(default=False, verbose_name='Afecta Inventario')
    
    # Usuario que crea el pedido
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Creado Por'
    )
    
    # Fechas de registro
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        unique_together = ['tenant', 'order_number']
    
    def __str__(self):
        return f"{self.order_number} - {self.cliente.obtener_nombre_completo()} - {self.get_document_type_display()}"
    
    def save(self, *args, **kwargs):
        """Guardar con cálculos automáticos"""
        # Calcular balance automáticamente
        self.balance = self.total - self.paid_amount
        
        # Actualizar estado de pago
        if self.paid_amount == 0:
            self.payment_status = 'pendiente'
        elif self.paid_amount >= self.total:
            self.payment_status = 'completo'
        else:
            self.payment_status = 'parcial'
        
        # Determinar si afecta inventario según tipo de documento
        self.affects_inventory = self.document_type == 'nota_venta'
        
        # Actualizar estado si está atrasado
        if self.status not in ['completado', 'cancelado'] and self.delivery_date:
            if timezone.now().date() > self.delivery_date:
                self.status = 'atrasado'
        
        super().save(*args, **kwargs)
        
        # Recalcular totales basado en items
        self.recalculate_totals()
    
    def clean(self):
        """Validaciones personalizadas"""
        # Validar que el cliente existe en el mismo tenant
        if self.cliente and self.tenant != self.cliente.tenant:
            raise ValidationError({'cliente': 'El cliente debe pertenecer al mismo tenant'})
        
        # Validar fechas
        if self.start_date and self.delivery_date and self.start_date > self.delivery_date:
            raise ValidationError({'delivery_date': 'La fecha de entrega debe ser posterior a la fecha de inicio'})
        
        # Validar campos requeridos según tipo de cliente
        if self.client_type == 'colegio':
            if not self.school_level:
                raise ValidationError({'school_level': 'El nivel es obligatorio para colegios'})
        
        # Validar montos
        if self.total < 0:
            raise ValidationError({'total': 'El total no puede ser negativo'})
        if self.paid_amount < 0:
            raise ValidationError({'paid_amount': 'El monto pagado no puede ser negativo'})
        if self.paid_amount > self.total:
            raise ValidationError({'paid_amount': 'El monto pagado no puede exceder el total'})
        
        # Validar contrato solo para tipo 'contrato'
        if self.document_type == 'contrato' and not self.contrato:
            raise ValidationError({'contrato': 'Debe seleccionar un contrato para pedidos de tipo contrato'})
        if self.document_type != 'contrato' and self.contrato:
            raise ValidationError({'contrato': 'Solo los pedidos de tipo contrato pueden tener un contrato relacionado'})
    
    def recalculate_totals(self):
        """Recalcular totales basado en los items del pedido"""
        items = self.items.all()
        subtotal = sum(item.subtotal for item in items)
        
        # Calcular IGV (18% en Perú)
        tax_rate = 0.18
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        # Actualizar solo si hay cambios significativos
        if abs(self.subtotal - subtotal) > 0.01:
            Order.objects.filter(id=self.id).update(
                subtotal=subtotal,
                tax=tax,
                total=total,
                balance=total - self.paid_amount
            )
    
    def get_scheduled_sessions(self):
        """Obtener lista de sesiones fotográficas programadas"""
        return self.scheduled_dates.get('sesiones_fotograficas', [])
    
    def get_scheduled_deliveries(self):
        """Obtener lista de entregas programadas"""
        return self.scheduled_dates.get('entregas', [])
    
    def add_scheduled_session(self, date, time, description=""):
        """Agregar una sesión fotográfica programada"""
        if 'sesiones_fotograficas' not in self.scheduled_dates:
            self.scheduled_dates['sesiones_fotograficas'] = []
        
        self.scheduled_dates['sesiones_fotograficas'].append({
            'fecha': date.isoformat(),
            'hora': time,
            'descripcion': description
        })
        self.save()
    
    def add_scheduled_delivery(self, date, time, description=""):
        """Agregar una entrega programada"""
        if 'entregas' not in self.scheduled_dates:
            self.scheduled_dates['entregas'] = []
        
        self.scheduled_dates['entregas'].append({
            'fecha': date.isoformat(),
            'hora': time,
            'descripcion': description
        })
        self.save()
    
    def mark_as_completed(self):
        """Marcar pedido como completado"""
        self.status = 'completado'
        self.save()
    
    def mark_as_cancelled(self):
        """Marcar pedido como cancelado"""
        self.status = 'cancelado'
        self.save()
    
    def update_status_based_on_dates(self):
        """Actualizar estado basado en las fechas"""
        if self.status in ['completado', 'cancelado']:
            return
        
        today = timezone.now().date()
        if self.delivery_date and today > self.delivery_date:
            self.status = 'atrasado'
        elif self.status == 'atrasado' and today <= self.delivery_date:
            self.status = 'pendiente'
        
        self.save()
    
    @property
    def is_overdue(self):
        """Verificar si el pedido está atrasado"""
        if self.status in ['completado', 'cancelado']:
            return False
        if self.delivery_date is None:
            return False  # o True, según la lógica que necesites
        return timezone.now().date() > self.delivery_date

    
    @property
    def days_until_delivery(self):
        """Días hasta la entrega"""
        if self.delivery_date:
            delta = self.delivery_date - timezone.now().date()
            return delta.days
        return None


class OrderItem(models.Model):
    """
    Modelo para items de pedidos (productos/servicios)
    """
    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Estudio Fotográfico')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Pedido', related_name='items')
    
    # Información del producto/servicio
    product_name = models.CharField(max_length=200, verbose_name='Nombre del Producto/Servicio')
    product_description = models.TextField(blank=True, verbose_name='Descripción')
    product_code = models.CharField(max_length=50, blank=True, verbose_name='Código del Producto')
    
    # Cantidad y precios
    quantity = models.IntegerField(default=1, verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Unitario')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Descuento (%)')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Subtotal')
    
    # Control de inventario
    affects_inventory = models.BooleanField(default=False, verbose_name='Afecta Inventario')
    inventory_item_id = models.IntegerField(null=True, blank=True, verbose_name='ID de Item de Inventario')
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity} - {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        """Guardar con cálculos automáticos"""
        # Calcular subtotal con descuento
        base_subtotal = self.quantity * self.unit_price
        discount_amount = base_subtotal * (self.discount_percentage / 100)
        self.subtotal = base_subtotal - discount_amount
        
        # Heredar afectación de inventario del pedido
        if self.order:
            self.affects_inventory = self.order.affects_inventory
            self.tenant = self.order.tenant
        
        super().save(*args, **kwargs)
        
        # Actualizar totales del pedido después de guardar el item
        if self.order:
            self.order.recalculate_totals()
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La cantidad debe ser mayor a 0'})
        if self.unit_price < 0:
            raise ValidationError({'unit_price': 'El precio unitario no puede ser negativo'})
        if self.discount_percentage < 0 or self.discount_percentage > 100:
            raise ValidationError({'discount_percentage': 'El descuento debe estar entre 0 y 100%'})
    
    @property
    def discount_amount(self):
        """Calcular monto del descuento"""
        quantity = self.quantity or 0
        unit_price = self.unit_price or 0
        discount_percentage = self.discount_percentage or 0
        base_subtotal = quantity * unit_price
        return base_subtotal * (discount_percentage / 100)



class OrderPayment(models.Model):
    """
    Modelo para pagos de pedidos
    """
    PAYMENT_METHOD_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('yape', 'Yape'),
        ('plin', 'Plin'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(verbose_name='Fecha de Pago')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='Método de Pago')
    reference_number = models.CharField(max_length=100, blank=True, verbose_name='Número de Referencia')
    notes = models.TextField(blank=True, verbose_name='Notas')
    
    # Usuario que registra el pago
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Registrado Por'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pago de Pedido'
        verbose_name_plural = 'Pagos de Pedido'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Pago {self.order.order_number} - S/ {self.amount}"
    
    def save(self, *args, **kwargs):
        """Guardar y actualizar el pedido"""
        super().save(*args, **kwargs)
        
        # Actualizar monto pagado del pedido
        total_paid = self.order.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        self.order.paid_amount = total_paid
        self.order.save()


class OrderStatusHistory(models.Model):
    """
    Historial de cambios de estado del pedido
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES, verbose_name='Estado Anterior')
    new_status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES, verbose_name='Estado Nuevo')
    reason = models.TextField(blank=True, verbose_name='Motivo del Cambio')
    
    # Usuario que realiza el cambio
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Cambiado Por'
    )
    
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.order.order_number}: {self.previous_status} → {self.new_status}"