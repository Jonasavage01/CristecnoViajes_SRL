import os
from pathlib import Path

# BASE_DIR: directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

###############################################################################

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-j&cn%x-g7wn0w5%zqd&9qo^&w+oxls2*9&ef3i5p4)sk2^iire'
)

# DEBUG: asegúrate de cambiarlo a False en producción.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS: en producción agrega aquí los dominios o IPs permitidos.
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split()  # Ej: 'localhost 127.0.0.1'

###############################################################################
# Aplicaciones instaladas
###############################################################################
INSTALLED_APPS = [
    # Apps por defecto de Django:
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_countries',  # App de terceros
     'django_cleanup.apps.CleanupConfig',
     'openpyxl',

    # Apps locales:
    'crm',
    'usuarios.apps.UsuariosConfig', 
    'dashboard.apps.DashboardConfig',
    'django_user_agents',
    
    
]

X_FRAME_OPTIONS = 'SAMEORIGIN'  # Cambiar de 'DENY' a 'SAMEORIGIN'

###############################################################################
# Middleware
###############################################################################
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',

]

###############################################################################
# Configuración de URLs y WSGI
###############################################################################
ROOT_URLCONF = 'CristecnoViajes_SRL.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directorios donde buscar plantillas
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Requerido por el admin y otros
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CristecnoViajes_SRL.wsgi.application'

###############################################################################
# Base de datos
###############################################################################
# Usamos SQLite para desarrollo; en producción, considera cambiar a PostgreSQL u otro.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

###############################################################################
# Validación de contraseñas
###############################################################################
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # Ejemplo: longitud mínima de 8 caracteres
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

###############################################################################
# Internacionalización
###############################################################################
LANGUAGE_CODE = 'en-us'
# Configurar zona horaria correcta
TIME_ZONE = 'America/Santo_Domingo'
USE_TZ = True
USE_I18N = True


###############################################################################
# Archivos estáticos y media
###############################################################################
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

###############################################################################
# Campo de clave primaria por defecto
###############################################################################
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

###############################################################################
# Configuración de Logging (básica)
###############################################################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

###############################################################################
# Configuración de Email
###############################################################################
# Durante el desarrollo, se pueden enviar los correos a la consola.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1']
if not DEBUG:
    # Redirigir todas las peticiones a HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Otras configuraciones de seguridad adicionales pueden agregarse aquí.
# Asegúrate de tener estas configuraciones
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://http://127.0.0.1:8000",
    
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
     "http://http://127.0.0.1:8000",
]

# settings.py
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

AUTH_USER_MODEL = 'usuarios.UsuarioPersonalizado'
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = '/usuarios/login/'

SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True  # Renovar la sesión con cada request
USE_I18N = True
USE_L10N = False  # Desactivar formato local para fechas
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d']  # Formatos de fecha aceptados
IPINFO_TOKEN = '839449f01be879'  # Tu token de ipinfo.io
USER_AGENTS_CACHE = 'default'  # Para mejor performance

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'your_app_name': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}