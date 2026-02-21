"""
Señales del Commerce App - Arte Ideas
Señales Django para automatización de procesos
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

# Importar desde módulos específicos
from .pedidos.models import Order, OrderItem, OrderPayment
from .inventario.models import BaseInventarioModel
from .models import Product  # Mantener Product para compatibilidad

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def update_order_balance(sender, instance, **kwargs):
    """
    Actualizar el saldo del pedido automáticamente
    saldo = total - a_cuenta
    """
    if instance.total is not None and instance.paid_amount is not None:
        instance.balance = instance.total - instance.paid_amount
        
        # Validar que el saldo no sea negativo
        if instance.balance < 0:
            instance.balance = 0


@receiver(pre_save, sender=Order)
def update_order_status_based_on_dates(sender, instance, **kwargs):
    """
    Actualizar el estado del pedido basado en las fechas
    
    - Si la fecha de entrega ya pasó y el estado es pendiente/en proceso → atrasado
    - Si el pedido está completado o cancelado, no cambiar el estado
    """
    today = timezone.now().date()
    
    # Solo actualizar si el pedido no está completado ni cancelado
    if instance.status not in ['completado', 'cancelado']:
        if instance.delivery_date and instance.delivery_date < today:
            instance.status = 'atrasado'
        elif instance.status == 'atrasado' and instance.delivery_date and instance.delivery_date >= today:
            # Si la fecha de entrega se actualizó al futuro, volver a pendiente
            instance.status = 'pendiente'


@receiver(pre_save, sender=Order)
def validate_order_document_type(sender, instance, **kwargs):
    """
    Validar el tipo de documento y establecer comportamiento por defecto
    
    - Proforma: No afecta inventario
    - Nota de venta: Afecta inventario
    - Contrato: Requiere contrato relacionado
    """
    if instance.document_type == 'proforma':
        instance.affects_inventory = False
    elif instance.document_type == 'nota_venta':
        instance.affects_inventory = True
    elif instance.document_type == 'contrato':
        # Verificar que tenga contrato relacionado
        if not instance.contrato:  # Cambio: contract → contrato
            logger.warning(f"Pedido {instance.order_number} de tipo contrato sin contrato relacionado")


@receiver(post_save, sender=Order)
def create_contract_events(sender, instance, created, **kwargs):
    """
    Crear eventos en la agenda cuando se crea un pedido de tipo contrato
    
    - Crear eventos para las sesiones fotográficas programadas
    - Crear eventos para las entregas programadas
    """
    if created and instance.document_type == 'contrato' and instance.contrato:
        try:
            # Importar modelo de eventos si existe
            # from apps.operations.models import Event
            
            scheduled_dates = instance.scheduled_dates or {}
            
            # Crear eventos para sesiones fotográficas
            sessions = scheduled_dates.get('sesiones_fotograficas', [])
            for i, session in enumerate(sessions):
                session_date = session.get('fecha')
                session_time = session.get('hora', '09:00')
                
                if session_date:
                    # Aquí se crearía el evento en la agenda
                    # Event.objects.create(
                    #     title=f"Sesión fotográfica - Pedido {instance.order_number}",
                    #     description=f"Sesión {i+1} para el pedido {instance.order_number}",
                    #     start_date=session_date,
                    #     start_time=session_time,
                    #     client=instance.client,
                    #     tenant=instance.tenant
                    # )
                    logger.info(f"Sesión fotográfica programada para {session_date}")
            
            # Crear eventos para entregas
            deliveries = scheduled_dates.get('entregas', [])
            for i, delivery in enumerate(deliveries):
                delivery_date = delivery.get('fecha')
                delivery_time = delivery.get('hora', '15:00')
                
                if delivery_date:
                    # Aquí se crearía el evento en la agenda
                    # Event.objects.create(
                    #     title=f"Entrega - Pedido {instance.order_number}",
                    #     description=f"Entrega {i+1} para el pedido {instance.order_number}",
                    #     start_date=delivery_date,
                    #     start_time=delivery_time,
                    #     client=instance.client,
                    #     tenant=instance.tenant
                    # )
                    logger.info(f"Entrega programada para {delivery_date}")
                    
        except Exception as e:
            logger.error(f"Error al crear eventos para pedido {instance.order_number}: {str(e)}")


@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Enviar notificaciones cuando se crea o actualiza un pedido
    
    - Notificar al cliente cuando se crea un pedido
    - Notificar cuando el pedido está atrasado
    - Notificar cuando el pedido está completado
    """
    try:
        if created:
            # Notificar creación de pedido
            if instance.cliente.email:  # Cambio: client → cliente
                subject = f"Nuevo pedido creado - {instance.order_number}"
                message = f"""
                Estimado/a {instance.cliente.obtener_nombre_completo()},
                
                Su pedido ha sido creado exitosamente.
                
                Detalles del pedido:
                - Número de pedido: {instance.order_number}
                - Tipo de documento: {instance.get_document_type_display()}
                - Fecha de entrega: {instance.delivery_date}
                - Total: S/ {instance.total}
                
                Gracias por confiar en nosotros.
                """
                # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.cliente.email])
                logger.info(f"Notificación de creación enviada para pedido {instance.order_number}")
        
        # Notificar pedido atrasado
        elif instance.status == 'atrasado' and instance.cliente.email:  # Cambio: delayed → atrasado
            subject = f"Pedido atrasado - {instance.order_number}"
            message = f"""
            Estimado/a {instance.cliente.obtener_nombre_completo()},
            
            Le informamos que su pedido {instance.order_number} está atrasado.
            La fecha de entrega programada era: {instance.delivery_date}
            
            Nos pondremos en contacto con usted para coordinar la entrega.
            
            Disculpe las molestias ocasionadas.
            """
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.cliente.email])
            logger.info(f"Notificación de atraso enviada para pedido {instance.order_number}")
        
        # Notificar pedido completado
        elif instance.status == 'completado' and instance.cliente.email:  # Cambio: completed → completado
            subject = f"Pedido completado - {instance.order_number}"
            message = f"""
            Estimado/a {instance.cliente.obtener_nombre_completo()},
            
            Nos complace informarle que su pedido {instance.order_number} ha sido completado.
            
            Gracias por su preferencia.
            """
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.cliente.email])
            logger.info(f"Notificación de completado enviada para pedido {instance.order_number}")
            
    except Exception as e:
        logger.error(f"Error al enviar notificaciones para pedido {instance.order_number}: {str(e)}")


@receiver(post_save, sender=OrderItem)
def update_order_totals_on_item_save(sender, instance, created, **kwargs):
    """
    Actualizar totales del pedido cuando se guarda un item
    
    - Recalcular subtotal, impuestos y total
    - Actualizar saldo
    """
    try:
        order = instance.order
        order.save()  # Esto disparará el método save del modelo que recalcula totales
        logger.info(f"Totales actualizados para pedido {order.order_number}")
    except Exception as e:
        logger.error(f"Error al actualizar totales para item {instance.id}: {str(e)}")


@receiver(post_delete, sender=OrderItem)
def update_order_totals_on_item_delete(sender, instance, **kwargs):
    """
    Actualizar totales del pedido cuando se elimina un item
    
    - Recalcular subtotal, impuestos y total
    - Actualizar saldo
    """
    try:
        order = instance.order
        order.save()  # Esto disparará el método save del modelo que recalcula totales
        logger.info(f"Totales actualizados después de eliminar item del pedido {order.order_number}")
    except Exception as e:
        logger.error(f"Error al actualizar totales después de eliminar item: {str(e)}")


@receiver(post_save, sender=Order)
def manage_inventory_on_order_save(sender, instance, created, **kwargs):
    """
    Gestionar inventario cuando se guarda un pedido
    
    - Para notas de venta: descontar del inventario
    - Para cancelaciones: devolver al inventario
    """
    try:
        if instance.document_type == 'nota_venta' and instance.affects_inventory:
            if created:
                # Descontar del inventario para pedidos nuevos
                for item in instance.items.all():
                    if item.affects_inventory and item.product_name:
                        # Buscar producto por nombre (simplificado)
                        try:
                            product = Product.objects.get(
                                name__iexact=item.product_name,
                                tenant=instance.tenant
                            )
                            if product.stock_quantity >= item.quantity:
                                product.stock_quantity -= item.quantity
                                product.save()
                                logger.info(f"Stock descontado para producto {product.name}")
                            else:
                                logger.warning(f"Stock insuficiente para producto {product.name}")
                        except Product.DoesNotExist:
                            logger.warning(f"Producto {item.product_name} no encontrado en inventario")
            
            elif instance.status == 'cancelado':  # Cambio: cancelled → cancelado
                # Devolver al inventario si se cancela
                for item in instance.items.all():
                    if item.affects_inventory and item.product_name:
                        try:
                            product = Product.objects.get(
                                name__iexact=item.product_name,
                                tenant=instance.tenant
                            )
                            product.stock_quantity += item.quantity
                            product.save()
                            logger.info(f"Stock devuelto para producto {product.name}")
                        except Product.DoesNotExist:
                            logger.warning(f"Producto {item.product_name} no encontrado en inventario")
                            
    except Exception as e:
        logger.error(f"Error al gestionar inventario para pedido {instance.order_number}: {str(e)}")


@receiver(pre_save, sender=Product)
def validate_product_stock(sender, instance, **kwargs):
    """
    Validar stock del producto
    
    - Advertir si el stock es negativo
    - Notificar si el stock está bajo
    """
    if instance.stock_quantity < 0:
        logger.warning(f"Stock negativo detectado para producto {instance.name}: {instance.stock_quantity}")
    
    if instance.stock_quantity <= instance.min_stock and instance.is_active:
        logger.warning(f"Stock bajo para producto {instance.name}: {instance.stock_quantity}")


def check_overdue_orders():
    """
    Función para verificar pedidos atrasados (puede ser llamada por un cron job)
    
    Esta función debe ser llamada periódicamente para actualizar el estado
    de los pedidos que están atrasados.
    """
    try:
        today = timezone.now().date()
        
        # Buscar pedidos que deberían estar marcados como atrasados
        overdue_orders = Order.objects.filter(
            delivery_date__lt=today,
            status__in=['pendiente', 'en_proceso']  # Cambio: pending, in_process → pendiente, en_proceso
        )
        
        # Actualizar estado a atrasado
        updated_count = overdue_orders.update(status='atrasado')  # Cambio: delayed → atrasado
        
        logger.info(f"Actualizados {updated_count} pedidos a estado 'atrasado'")
        
        return updated_count
        
    except Exception as e:
        logger.error(f"Error al verificar pedidos atrasados: {str(e)}")
        return 0


def send_daily_order_summary():
    """
    Función para enviar resumen diario de pedidos (puede ser llamada por un cron job)
    
    Envía un resumen diario con:
    - Pedidos nuevos
    - Pedidos completados
    - Pedidos atrasados
    """
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Contar pedidos del día anterior
        new_orders = Order.objects.filter(created_at__date=yesterday).count()
        completed_orders = Order.objects.filter(
            updated_at__date=yesterday,
            status='completado'  # Cambio: completed → completado
        ).count()
        overdue_orders = Order.objects.filter(status='atrasado').count()  # Cambio: delayed → atrasado
        
        # Aquí se podría enviar un email con el resumen
        # o guardar en un log para revisión
        
        logger.info(f"Resumen diario: {new_orders} nuevos, {completed_orders} completados, {overdue_orders} atrasados")
        
        return {
            'new_orders': new_orders,
            'completed_orders': completed_orders,
            'overdue_orders': overdue_orders
        }
        
    except Exception as e:
        logger.error(f"Error al generar resumen diario: {str(e)}")
        return None