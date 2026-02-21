"""
Señales del Módulo de Pedidos - Arte Ideas Commerce
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum

from .models import Order, OrderItem, OrderPayment, OrderStatusHistory

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrderPayment)
def update_order_payment_totals(sender, instance, created, **kwargs):
    """
    Actualizar totales de pago del pedido cuando se registra un pago
    """
    try:
        order = instance.order
        
        # Recalcular total pagado
        total_paid = order.payments.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        order.paid_amount = total_paid
        order.save()
        
        logger.info(f"Pago registrado para pedido {order.order_number}: S/ {instance.amount}")
        
    except Exception as e:
        logger.error(f"Error al actualizar totales de pago: {str(e)}")


@receiver(post_save, sender=Order)
def create_status_history_on_status_change(sender, instance, created, **kwargs):
    """
    Crear registro en historial cuando cambia el estado del pedido
    """
    if not created:  # Solo para actualizaciones
        try:
            # Obtener el estado anterior de la base de datos
            if instance.pk:
                old_instance = Order.objects.get(pk=instance.pk)
                if hasattr(old_instance, '_state') and old_instance.status != instance.status:
                    # Crear registro en historial
                    OrderStatusHistory.objects.create(
                        order=instance,
                        previous_status=old_instance.status,
                        new_status=instance.status,
                        reason='Cambio automático del sistema',
                        changed_by=getattr(instance, '_changed_by', None)
                    )
                    
                    logger.info(f"Estado del pedido {instance.order_number} cambió de {old_instance.status} a {instance.status}")
                    
        except Exception as e:
            logger.error(f"Error al crear historial de estado: {str(e)}")


@receiver(pre_save, sender=Order)
def validate_order_dates(sender, instance, **kwargs):
    """
    Validar fechas del pedido antes de guardar
    """
    if instance.start_date and instance.delivery_date:
        if instance.start_date > instance.delivery_date:
            logger.warning(f"Pedido {instance.order_number}: Fecha de inicio posterior a fecha de entrega")
    
    # Validar que la fecha de entrega no sea en el pasado (solo para pedidos nuevos)
    if not instance.pk and instance.delivery_date:
        today = timezone.now().date()
        if instance.delivery_date < today:
            logger.warning(f"Pedido {instance.order_number}: Fecha de entrega en el pasado")


@receiver(post_save, sender=OrderItem)
def recalculate_order_totals_on_item_change(sender, instance, **kwargs):
    """
    Recalcular totales del pedido cuando cambia un item
    """
    try:
        order = instance.order
        order.recalculate_totals()
        logger.info(f"Totales recalculados para pedido {order.order_number}")
    except Exception as e:
        logger.error(f"Error al recalcular totales: {str(e)}")


@receiver(post_delete, sender=OrderItem)
def recalculate_order_totals_on_item_delete(sender, instance, **kwargs):
    """
    Recalcular totales del pedido cuando se elimina un item
    """
    try:
        order = instance.order
        order.recalculate_totals()
        logger.info(f"Totales recalculados después de eliminar item del pedido {order.order_number}")
    except Exception as e:
        logger.error(f"Error al recalcular totales después de eliminar item: {str(e)}")