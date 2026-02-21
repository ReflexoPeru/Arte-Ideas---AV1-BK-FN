"""
Analytics Models - Arte Ideas
"""
from django.db import models
from apps.core.models import BaseModel


class ReportConfiguration(BaseModel):
    """
    Configuración de reportes del sistema
    Permite personalizar parámetros por defecto para los reportes
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre de la Configuración',
        help_text='Nombre descriptivo para esta configuración'
    )
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('ventas', 'Ventas'),
            ('inventario', 'Inventario'),
            ('produccion', 'Producción'),
            ('clientes', 'Clientes'),
            ('financiero', 'Financiero'),
            ('contratos', 'Contratos'),
        ],
        verbose_name='Categoría',
        help_text='Categoría de reporte a la que aplica esta configuración'
    )
    dias_por_defecto = models.IntegerField(
        default=30,
        verbose_name='Días por Defecto',
        help_text='Número de días hacia atrás para el rango de fechas por defecto'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si esta configuración está activa'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción adicional de la configuración'
    )
    
    class Meta:
        verbose_name = 'Configuración de Reporte'
        verbose_name_plural = 'Configuraciones de Reportes'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

