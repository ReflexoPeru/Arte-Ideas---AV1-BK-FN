from django.db import models
from datetime import date

# Create your models here.

class Activo(models.Model):
    CATEGORIAS = [
        ('impresora', 'Impresora'),
        ('equipo de oficina', 'Equipo de Oficina'),
        ('maquinaria', 'Maquinaria'),
        ('herramienta', 'Herramienta'),
        ('vehiculo', 'Vehículo'),
    ]
    TIPOS_PAGO = [
        ('contado', 'Contado'),
        ('financiado', 'Financiado'),
        ('leasing', 'Leasing'),
    ]
    ESTADOS = [
        ('activo', 'Activo'),
        ('en mantenimiento', 'En Mantenimiento'),
        ('inactivo', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    proveedor = models.CharField(max_length=255)
    fecha_compra = models.DateField()
    costo_total = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_pago = models.CharField(max_length=20, choices=TIPOS_PAGO)
    vida_util = models.PositiveIntegerField(help_text="Vida útil en meses")
    depreciacion_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS)

    def __str__(self):
        return self.nombre


class Financiamiento(models.Model):
    TIPOS_PAGO = [
        ('financiado', 'Financiado'),
        ('leasing', 'Leasing'),
    ]
    ESTADOS = [
        ('activo', 'Activo'),
        ('pagado', 'Pagado'),
        ('mora', 'Mora'),
    ]

    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='financiamientos')
    tipo_pago = models.CharField(max_length=20, choices=TIPOS_PAGO)
    entidad_financiera = models.CharField(max_length=255)
    monto_financiado = models.DecimalField(max_digits=12, decimal_places=2)
    cuotas_totales = models.PositiveIntegerField()
    cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS)

    def __str__(self):
        return f"{self.activo.nombre} - {self.get_tipo_pago_display()}"


class Mantenimiento(models.Model):
    TIPOS_MANTENIMIENTO = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('emergencia', 'Emergencia'),
    ]
    ESTADOS_ACTIVO = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ("mantenimiento", "Mantenimiento"),
    ]
    ESTADOS_MANTENIMIENTO = [
        ('programado', 'Programado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='mantenimientos')
    tipo_mantenimiento = models.CharField(max_length=20, choices=TIPOS_MANTENIMIENTO)
    fecha_mantenimiento = models.DateField()
    proveedor = models.CharField(max_length=255)
    costo = models.DecimalField(max_digits=12, decimal_places=2)
    estado_del_mantenimiento = models.CharField(max_length=20, choices=ESTADOS_MANTENIMIENTO, default='programado')
    estado_del_activo = models.CharField(max_length=20, choices=ESTADOS_ACTIVO, default='activo')
    proxima_fecha_mantenimiento = models.DateField(default=date.today)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.activo.nombre} - {self.get_tipo_mantenimiento_display()} - {self.fecha_mantenimiento}"


class Repuesto(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
    ]
    CATEGORIAS = [
        ('insumos impresoras', 'Insumos Impresoras'),
        ('repuestos impresoras', 'Repuestos Impresoras'),
        ('insumos camaras', 'Insumos Camaras'),
        ('repuestos camaras', 'Repuestos Camaras'),
        ('herramientas', 'Herramientas'),
        ('otros', 'Otros'),
    ]
    UBICACIONES = [
        ('almacen A', 'Almacen A'),
        ('almacen B', 'Almacen B'),
        ("estanteria 1", "Estanteria 1"),
        ("estanteria 2", "Estanteria B"),
        ("bodega", "Bodega"),
    ]

    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='general')
    ubicacion = models.CharField(max_length=20, choices=UBICACIONES, default='almacen A')
    proveedor = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255, default='0000000000')
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descripcion = models.TextField(default='')

    def __str__(self):
        return f"{self.nombre} - {self.codigo} ({self.categoria})"
    
    class Meta:
        verbose_name = 'Repuesto'
        verbose_name_plural = 'Repuestos'
        ordering = ['nombre']