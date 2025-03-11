import requests
import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

def get_ip_geolocation(ip_address):
    """Obtiene datos de geolocalización con manejo especial para entornos de desarrollo"""
    
    # Mock para pruebas en local
    if settings.DEBUG and ip_address == '127.0.0.1':
        logger.warning("IP local detectada en modo DEBUG - Usando datos de prueba")
        return {
            'city': 'Buenos Aires',
            'region': 'CABA',
            'country': 'AR',
            'loc': '-34.6132,-58.3772',
            'postal': '1000',
            'timezone': 'America/Argentina/Buenos_Aires'
        }

    # Validación inicial
    if not ip_address:
        logger.debug("IP no proporcionada")
        return None
        
    # Normalización de IP
    ips = ip_address.split(',')
    clean_ip = ips[0].strip() if ips else ip_address.strip()
    
    # Excluir direcciones privadas
    private_patterns = [
        '127.0.0.1', '::1', 'localhost',
        '10.', '192.168.', '172.16.', '172.31.'
    ]
    if any(clean_ip.startswith(prefix) for prefix in private_patterns):
        logger.warning(f"IP privada detectada: {clean_ip}")
        return None

    # Verificación de token
    token = getattr(settings, 'IPINFO_TOKEN', None)
    if not token:
        raise ImproperlyConfigured("Falta configurar IPINFO_TOKEN en settings")

    try:
        response = requests.get(
            f'https://ipinfo.io/{clean_ip}/json',
            params={'token': token},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        # Validación de datos mínimos
        required_fields = ['country', 'loc']
        if not all(field in data for field in required_fields):
            logger.warning(f"Datos incompletos para {clean_ip}: {data}")
            return None

        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error en solicitud a ipinfo.io: {str(e)}", exc_info=True)
        return None
    except ValueError as e:
        logger.error(f"Respuesta inválida de ipinfo.io: {str(e)}", exc_info=True)
        return None