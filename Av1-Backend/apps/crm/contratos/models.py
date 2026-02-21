"""
Modelos de Contratos - Arte Ideas CRM
Gestión de contratos de servicios fotográficos
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.core.models import Tenant


class Contrato(models.Model):
    """
    Modelo para contratos de servicios fotográficos
    Relacionado con pedidos cuando el tipo de documento es 'Contrato'
    """
    ESTADO_CONTRATO_CHOICES = [
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_SERVICIO_CHOICES = [
        ('fotografia', 'Servicio Fotografía'),
        ('enmarcado', 'Enmarcado'),
        ('graduaciones', 'Graduaciones'),
        ('laser', 'Corte Láser'),
        ('evento', 'Evento'),
        ('personalizado', 'Personalizado'),
    ]
    
    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Estudio Fotográfico')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, verbose_name='Cliente', related_name='contratos')
    
    # Información del contrato
    numero_contrato = models.CharField(max_length=50, verbose_name='Número de Contrato')
    titulo = models.CharField(max_length=200, verbose_name='Título del Contrato')
    descripcion = models.TextField(verbose_name='Descripción')
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES, verbose_name='Tipo de Servicio')
    
    # Fechas importantes
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de Fin')
    
    # Montos
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto Total')
    adelanto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Adelanto')
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Saldo Pendiente')
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CONTRATO_CHOICES,
        default='borrador',
        verbose_name='Estado'
    )
    
    # Archivos
    documento_contrato = models.FileField(upload_to='contratos/', blank=True, null=True, verbose_name='Documento del Contrato')
    
    # Fechas de registro
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-creado_en']
        unique_together = ['tenant', 'numero_contrato']
    
    def __str__(self):
        return f"{self.numero_contrato} - {self.titulo}"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError({'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'})
        
        if self.adelanto and self.monto_total and self.adelanto > self.monto_total:
            raise ValidationError({'adelanto': 'El adelanto no puede ser mayor al monto total'})

        # Validación de unicidad por tenant antes de guardar para mostrar error claro en el campo
        if self.tenant_id and self.numero_contrato:
            qs = Contrato.objects.filter(tenant_id=self.tenant_id, numero_contrato=self.numero_contrato)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'numero_contrato': 'Este número de contrato ya existe en su estudio.'})
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones y cálculos automáticos"""
        # Calcular saldo pendiente
        if self.monto_total and self.adelanto:
            self.saldo_pendiente = self.monto_total - self.adelanto
        else:
            self.saldo_pendiente = self.monto_total or 0
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def porcentaje_adelanto(self):
        """Calcular porcentaje de adelanto"""
        if self.monto_total and self.adelanto:
            return (self.adelanto / self.monto_total) * 100
        return 0
    
    @property
    def esta_vencido(self):
        """Verificar si el contrato está vencido"""
        from django.utils import timezone
        return self.fecha_fin < timezone.now().date() and self.estado == 'activo'


class ClausulaContrato(models.Model):
    """
    Cláusulas específicas del contrato
    """
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='clausulas')
    numero_clausula = models.PositiveIntegerField(verbose_name='Número de Cláusula')
    titulo = models.CharField(max_length=200, verbose_name='Título de la Cláusula')
    contenido = models.TextField(verbose_name='Contenido de la Cláusula')
    
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cláusula de Contrato'
        verbose_name_plural = 'Cláusulas de Contrato'
        ordering = ['numero_clausula']
        unique_together = ['contrato', 'numero_clausula']
    
    def __str__(self):
        return f"Cláusula {self.numero_clausula}: {self.titulo}"


class PagoContrato(models.Model):
    """
    Pagos realizados para el contrato
    """
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('yape', 'Yape'),
        ('plin', 'Plin'),
        ('otro', 'Otro'),
    ]
    
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateField(verbose_name='Fecha de Pago')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto Pagado')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, verbose_name='Método de Pago')
    numero_operacion = models.CharField(max_length=100, blank=True, verbose_name='Número de Operación')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    
    # Usuario que registra el pago
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='Registrado Por'
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pago de Contrato'
        verbose_name_plural = 'Pagos de Contrato'
        ordering = ['-fecha_pago']
    
    def __str__(self):
        return f"Pago {self.contrato.numero_contrato} - S/ {self.monto}"


class EstadoContrato(models.Model):
    """
    Historial de cambios de estado del contrato
    """
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=20, choices=Contrato.ESTADO_CONTRATO_CHOICES, verbose_name='Estado Anterior')
    estado_nuevo = models.CharField(max_length=20, choices=Contrato.ESTADO_CONTRATO_CHOICES, verbose_name='Estado Nuevo')
    motivo = models.TextField(blank=True, verbose_name='Motivo del Cambio')
    
    # Usuario que realiza el cambio
    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='Cambiado Por'
    )
    
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Estado de Contrato'
        verbose_name_plural = 'Estados de Contrato'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.contrato.numero_contrato}: {self.estado_anterior} → {self.estado_nuevo}"