from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth.models import AnonymousUser
import logging
from .models import UsuarioPersonalizado, UserActivityLog
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    try:
        UserActivityLog.objects.create(
            user=user,
            activity_type=UserActivityLog.ActivityType.LOGIN,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )
    except Exception as e:
        logger.error(f"Error al registrar login: {str(e)}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if isinstance(user, UsuarioPersonalizado) and user.is_authenticated:
        UserActivityLog.objects.create(
            user=user,
            activity_type=UserActivityLog.ActivityType.LOGOUT,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(
        f"Login fallido | Usuario intentado: {credentials.get('username', 'None')} | "
        f"IP: {request.META.get('REMOTE_ADDR')} | "
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Desconocido')}"
    )

@receiver(models.signals.post_save, sender=UsuarioPersonalizado)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Nuevo usuario creado | "
            f"Usuario: {instance.username} | "
            f"Creado por: {instance._created_by if hasattr(instance, '_created_by') else 'Sistema'}"
        )