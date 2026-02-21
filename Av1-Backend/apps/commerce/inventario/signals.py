"""
Señales del Módulo de Inventario - Arte Ideas Commerce
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F

from .models import (
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
)

logger = logging.getLogger(__name__)

# Lista de todos los modelos de inventario
INVENTORY_MODELS = [
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
]


def create_inventory_signals():
    """
    Crear señales para todos los modelos de inventario
    """
    for model in INVENTORY_MODELS:
        
        @receiver(pre_save, sender=model)
        def validate_inventory_stock(sender, instance, **kwargs):
            """
            Validar stock del producto de inventario
            """
            if instance.stock_disponible < 0:
                logger.warning(f"Stock negativo detectado para {instance.nombre_producto}: {instance.stock_disponible}")
            
            if instance.alerta_stock and instance.is_active:
                logger.warning(f"Stock bajo para {instance.nombre_producto}: {instance.stock_disponible} (mínimo: {instance.stock_minimo})")
        
        @receiver(post_save, sender=model)
        def notify_low_stock(sender, instance, created, **kwargs):
            """
            Notificar cuando un producto tiene stock bajo
            """
            if instance.alerta_stock and instance.is_active:
                try:
                    # Aquí se podría enviar una notificación por email
                    subject = f"Alerta de Stock Bajo - {instance.nombre_producto}"
                    message = f"""
                    Producto: {instance.nombre_producto}
                    Stock actual: {instance.stock_disponible}
                    Stock mínimo: {instance.stock_minimo}
                    Categoría: {sender._meta.verbose_name}
                    
                    Es necesario reabastecer este producto.
                    """
                    
                    # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['admin@estudio.com'])
                    logger.info(f"Alerta de stock bajo enviada para {instance.nombre_producto}")
                    
                except Exception as e:
                    logger.error(f"Error al enviar alerta de stock bajo: {str(e)}")


# Crear las señales para todos los modelos
create_inventory_signals()


@receiver(pre_save, sender=MolduraListon)
def validate_moldura_liston_specific(sender, instance, **kwargs):
    """
    Validaciones específicas para Moldura Listón
    """
    if instance.costo_unitario <= 0:
        logger.warning(f"Costo unitario inválido para moldura {instance.nombre_producto}: {instance.costo_unitario}")


@receiver(pre_save, sender=Minilab)
def validate_minilab_specific(sender, instance, **kwargs):
    """
    Validaciones específicas para Minilab
    """
    if instance.tipo_insumo == 'quimica' and instance.stock_disponible > 100:
        logger.info(f"Stock alto de químicos detectado: {instance.nombre_producto} - {instance.stock_disponible}")


@receiver(pre_save, sender=CorteLaser)
def validate_corte_laser_specific(sender, instance, **kwargs):
    """
    Validaciones específicas para Corte Láser
    """
    if instance.tipo == 'acrilico' and instance.stock_disponible <= instance.stock_minimo:
        logger.warning(f"Stock crítico de acrílico: {instance.nombre_producto}")


def check_inventory_alerts():
    """
    Función para verificar alertas de inventario (puede ser llamada por un cron job)
    """
    try:
        total_alerts = 0
        
        for model in INVENTORY_MODELS:
            alerts = model.objects.filter(
                stock_disponible__lte=F('stock_minimo'),
                is_active=True
            )
            
            count = alerts.count()
            total_alerts += count
            
            if count > 0:
                logger.info(f"{model._meta.verbose_name}: {count} productos con stock bajo")
        
        logger.info(f"Total de alertas de inventario: {total_alerts}")
        return total_alerts
        
    except Exception as e:
        logger.error(f"Error al verificar alertas de inventario: {str(e)}")
        return 0


def generate_inventory_report():
    """
    Generar reporte de inventario
    """
    try:
        report = {
            'total_productos': 0,
            'valor_total': 0,
            'alertas_stock': 0,
            'categorias': {}
        }
        
        for model in INVENTORY_MODELS:
            productos = model.objects.filter(is_active=True)
            categoria = model._meta.verbose_name_plural
            
            count = productos.count()
            valor = sum(p.costo_total for p in productos)
            alertas = productos.filter(stock_disponible__lte=F('stock_minimo')).count()
            
            report['total_productos'] += count
            report['valor_total'] += float(valor)
            report['alertas_stock'] += alertas
            
            report['categorias'][categoria] = {
                'productos': count,
                'valor': float(valor),
                'alertas': alertas
            }
        
        logger.info(f"Reporte de inventario generado: {report['total_productos']} productos, S/ {report['valor_total']:.2f}")
        return report
        
    except Exception as e:
        logger.error(f"Error al generar reporte de inventario: {str(e)}")
        return None