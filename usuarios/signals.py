from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .services import get_ip_geolocation 
from django.contrib.auth.models import AnonymousUser
import logging
from .services import get_ip_geolocation
from .models import UsuarioPersonalizado, UserActivityLog
from django.db import models
from django.utils import timezone
from user_agents import parse
from django.conf import settings

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    try:
        # Obtener IP con override para desarrollo
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        # Override solo si está en DEBUG y la IP es local
        if settings.DEBUG and ip_address in ['127.0.0.1', '::1']:
            ip_address = '200.215.234.10'  # IP de prueba
        
        user_agent_str = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_str)
        
        # Obtener datos de geolocalización
        geo_data = get_ip_geolocation(ip_address)
        
        # Crear registro de actividad
        activity = UserActivityLog.objects.create(
            user=user,
            activity_type=UserActivityLog.ActivityType.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent_str[:255],
            city=geo_data.get('city') if geo_data else None,
            region=geo_data.get('region') if geo_data else None,
            country=geo_data.get('country') if geo_data else None,
            loc=geo_data.get('loc') if geo_data else None,
            postal=geo_data.get('postal') if geo_data else None,
            timezone=geo_data.get('timezone') if geo_data else None,
            device_type=user_agent.device.family if user_agent.device else None,
            browser=user_agent.browser.family,
            os=user_agent.os.family,
            is_mobile=user_agent.is_mobile,
            is_tablet=user_agent.is_tablet,
            is_touch_capable=user_agent.is_touch_capable,
            is_pc=user_agent.is_pc,
            is_bot=user_agent.is_bot
        )

        # Actualizar última IP del usuario
        user.last_login_ip = ip_address
        user.save(update_fields=['last_login_ip'])
        
        # Logs de depuración
        logger.debug(f"Login exitoso desde IP: {ip_address}")
        logger.debug(f"Datos de geolocalización: {geo_data}")

    except Exception as e:
        logger.error(f"Error registrando actividad: {str(e)}", exc_info=True)


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