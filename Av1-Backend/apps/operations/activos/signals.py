from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from datetime import date, timedelta
from decimal import Decimal
from .models import Activo, Financiamiento

@receiver(post_save, sender=Activo)
def crear_o_actualizar_financiamiento(sender, instance, created, **kwargs):
    """
    Crea automáticamente un registro de financiamiento cuando se crea/actualiza 
    un activo con tipo de pago 'financiado' o 'leasing'
    """
    if instance.tipo_pago in ['financiado', 'leasing']:
        # Verificar si ya existe un financiamiento para este activo
        financiamiento, financiamiento_created = Financiamiento.objects.get_or_create(
            activo=instance,
            defaults={
                'tipo_pago': instance.tipo_pago,
                'entidad_financiera': 'Por definir',
                'monto_financiado': instance.costo_total * Decimal('0.8') if instance.tipo_pago == 'financiado' else instance.costo_total,
                'cuotas_totales': 24 if instance.tipo_pago == 'financiado' else 60,
                'cuota_mensual': (instance.costo_total * Decimal('0.8')) / 24 if instance.tipo_pago == 'financiado' else instance.costo_total / 60,
                'fecha_inicio': date.today(),
                'fecha_fin': date.today() + timedelta(days=730) if instance.tipo_pago == 'financiado' else date.today() + timedelta(days=1825),
                'estado': 'activo'
            }
        )
        
        # Si no se creó (ya existía), actualizar el tipo de pago por si cambió
        if not financiamiento_created:
            financiamiento.tipo_pago = instance.tipo_pago
            financiamiento.save()
            
    else:
        # Si el activo ya no es financiado/leasing, eliminar el financiamiento
        Financiamiento.objects.filter(activo=instance).delete()

@receiver(post_delete, sender=Activo)
def eliminar_financiamiento(sender, instance, **kwargs):
    """
    Elimina el registro de financiamiento cuando se elimina un activo
    """
    Financiamiento.objects.filter(activo=instance).delete()