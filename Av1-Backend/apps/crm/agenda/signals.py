from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Evento, Cita, Recordatorio


@receiver(pre_save, sender=Evento)
def validar_fechas_evento(sender, instance, **kwargs):
    if instance.fecha_fin <= instance.fecha_inicio:
        from django.core.exceptions import ValidationError
        raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")


@receiver(post_save, sender=Evento)
def crear_recordatorios_automaticos(sender, instance, created, **kwargs):
    if created and instance.recordatorio_minutos and instance.recordatorio_minutos > 0:
        mensaje = f"""
        Recordatorio: {instance.titulo}
        Fecha: {instance.fecha_inicio.strftime('%d/%m/%Y %H:%M')}
        Tipo: {instance.get_tipo_evento_display()}
        Prioridad: {instance.get_prioridad_display()}
        {instance.descripcion or 'Sin descripción'}
        """
        Recordatorio.objects.create(
            evento=instance,
            tipo_recordatorio='sistema',
            minutos_antes=instance.recordatorio_minutos,
            destinatario=instance.asignado_a,
            mensaje=mensaje.strip(),
        )


@receiver(post_save, sender=Cita)
def actualizar_evento_cita(sender, instance, created, **kwargs):
    if not created:
        if instance.estado_cita == 'completada':
            instance.evento.estado = 'completado'
            instance.evento.save()
        elif instance.estado_cita == 'cancelada':
            instance.evento.estado = 'cancelado'
            instance.evento.save()


@receiver(post_save, sender=Recordatorio)
def enviar_recordatorio(sender, instance, created, **kwargs):
    if not created and instance.debe_enviarse and not instance.enviado:
        try:
            if instance.tipo_recordatorio == 'email':
                send_mail(
                    subject=f'Recordatorio: {instance.evento.titulo}',
                    message=instance.mensaje,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.destinatario.email],
                    fail_silently=False,
                )
            instance.enviado = True
            instance.fecha_envio = timezone.now()
            instance.save(update_fields=['enviado', 'fecha_envio'])
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar recordatorio: {e}")