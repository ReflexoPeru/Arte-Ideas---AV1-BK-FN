"""
Modelos del Módulo de Producción - Arte Ideas Operations
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

from apps.core.models import Tenant, User
from apps.crm.models import Cliente
from apps.commerce.models import Order


class OrdenProduccion(models.Model):
    """
    Modelo para órdenes de producción del estudio fotográfico
    Gestiona el flujo de trabajo interno desde pedidos hasta entrega
    """
    TIPO_CHOICES = [
        ('enmarcado', 'Enmarcado'),
        ('minilab', 'Minilab'),
        ('graduacion', 'Graduación'),
        ('corte_laser', 'Corte Láser'),
        ('edicion_digital', 'Edición Digital'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('terminado', 'Terminado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('normal', 'Normal'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Estudio Fotográfico', related_name='ordenes_produccion')
    
    # Información básica
    numero_op = models.CharField(max_length=20, verbose_name='Número de OP')
    
    # Relaciones
    pedido = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='Pedido', related_name='ordenes_produccion')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name='Cliente', related_name='ordenes_produccion')
    operario = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        verbose_name='Operario Asignado',
        related_name='ordenes_asignadas',
        limit_choices_to={'role': 'operario'}
    )
    
    # Detalles de la orden
    descripcion = models.TextField(verbose_name='Descripción del Trabajo')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Producción')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='normal', verbose_name='Prioridad')
    
    # Fechas
    fecha_estimada = models.DateField(verbose_name='Fecha Estimada de Finalización')
    fecha_inicio_real = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Inicio Real')
    fecha_finalizacion_real = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Finalización Real')
    
    # Información adicional
    notas_operario = models.TextField(blank=True, verbose_name='Notas del Operario')
    materiales_utilizados = models.JSONField(default=dict, blank=True, verbose_name='Materiales Utilizados')
    tiempo_estimado_horas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Tiempo Estimado (horas)')
    tiempo_real_horas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Tiempo Real (horas)')
    
    # Usuario que crea la orden
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Creado Por',
        related_name='ordenes_creadas'
    )
    
    # Fechas de auditoría
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Creado en')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Actualizado en')
    
    class Meta:
        verbose_name = "Orden de Producción"
        verbose_name_plural = "Órdenes de Producción"
        ordering = ['-creado_en']
        unique_together = ['tenant', 'numero_op']
    
    def __str__(self):
        return f"{self.numero_op} - {self.get_estado_display()} - {self.cliente.obtener_nombre_completo()}"
    
    def save(self, *args, **kwargs):
        """Guardar con lógica automática"""
        # Autocompletar cliente según pedido seleccionado
        if self.pedido and not self.cliente_id:
            self.cliente = self.pedido.cliente
        
        # Autocompletar tenant según pedido
        if self.pedido and not self.tenant_id:
            self.tenant = self.pedido.tenant
        
        # Actualizar fechas según estado
        if self.estado == 'en_proceso' and not self.fecha_inicio_real:
            self.fecha_inicio_real = timezone.now()
        elif self.estado == 'terminado' and not self.fecha_finalizacion_real:
            self.fecha_finalizacion_real = timezone.now()
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validaciones personalizadas"""
        # Validar que el pedido y cliente pertenezcan al mismo tenant
        if self.pedido and self.tenant != self.pedido.tenant:
            raise ValidationError({'pedido': 'El pedido debe pertenecer al mismo tenant'})
        
        if self.cliente and self.tenant != self.cliente.tenant:
            raise ValidationError({'cliente': 'El cliente debe pertenecer al mismo tenant'})
        
        # Validar que el operario pertenezca al mismo tenant
        if self.operario and self.tenant != self.operario.tenant:
            raise ValidationError({'operario': 'El operario debe pertenecer al mismo tenant'})
        
        # Validar fecha estimada
        if self.fecha_estimada and self.fecha_estimada < date.today():
            if not self.pk:  # Solo para nuevas órdenes
                raise ValidationError({'fecha_estimada': 'La fecha estimada no puede ser en el pasado'})
        
        # Validar tiempos
        if self.tiempo_real_horas and self.tiempo_real_horas < 0:
            raise ValidationError({'tiempo_real_horas': 'El tiempo real no puede ser negativo'})
    
    @property
    def is_vencida(self):
        """Verificar si la orden está vencida"""
        if self.estado in ['terminado', 'entregado', 'cancelado']:
            return False
        return date.today() > self.fecha_estimada
    
    @property
    def dias_hasta_vencimiento(self):
        """Días hasta el vencimiento"""
        if self.fecha_estimada:
            delta = self.fecha_estimada - date.today()
            return delta.days
        return None
    
    def marcar_iniciado(self):
        """Marcar orden como iniciada"""
        if self.estado == 'pendiente':
            self.estado = 'en_proceso'
            self.fecha_inicio_real = timezone.now()
            self.save()
    
    def marcar_terminado(self):
        """Marcar orden como terminada"""
        if self.estado == 'en_proceso':
            self.estado = 'terminado'
            self.fecha_finalizacion_real = timezone.now()
            self.save()
    
    def marcar_entregado(self):
        """Marcar orden como entregada"""
        if self.estado == 'terminado':
            self.estado = 'entregado'
            self.save()
    
    def calcular_eficiencia(self):
        """Calcular eficiencia comparando tiempo estimado vs real"""
        if self.tiempo_estimado_horas and self.tiempo_real_horas:
            if self.tiempo_real_horas > 0:
                return (self.tiempo_estimado_horas / self.tiempo_real_horas) * 100
        return None