from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from django.core.validators import FileExtensionValidator

class UsuarioPersonalizado(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', _('Administrador')
        CLIENTES = 'clientes', _('Gestor de Clientes')
        CONTABILIDAD = 'contabilidad', _('Contabilidad')
        RESERVAS = 'reservas', _('Gestor de Reservas')
    
    rol = models.CharField(
        _('Rol'),
        max_length=20,
        choices=Roles.choices,
        default=Roles.ADMIN
    )
    telefono = models.CharField(
        _('Teléfono'),
        max_length=20,
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField(
        _('Fecha de creación'),
        auto_now_add=True
    )
    last_seen = models.DateTimeField(
        _('Última actividad'), 
        null=True, 
        blank=True
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('Grupos'),
        blank=True,
        related_name="usuarios_personalizados",
        related_query_name="usuario_personalizado"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('Permisos de usuario'),
        blank=True,
        related_name="usuarios_personalizados",
        related_query_name="usuario_personalizado"
    )
    login_attempts = models.PositiveIntegerField(
        _('Intentos fallidos'),
        default=0,
        help_text=_('Número de intentos fallidos de inicio de sesión')
    )
    last_login_ip = models.GenericIPAddressField(
        _('Última IP de acceso'),
        null=True, 
        blank=True
    )

    @property
    def is_online(self):
        return self.last_seen and self.last_seen >= timezone.now() - timezone.timedelta(minutes=2)
    
    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ('-fecha_creacion',)

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})" if self.get_full_name() else f"{self.username} ({self.rol})"

class UserActivityLog(models.Model):
    class ActivityType(models.TextChoices):
        LOGIN = 'login', _('Inicio de sesión')
        LOGOUT = 'logout', _('Cierre de sesión')
    
    user = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=10, choices=ActivityType.choices)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha/Hora'))
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    loc = models.CharField(max_length=50, null=True, blank=True, 
                         help_text='Latitud/Longitud')
    postal = models.CharField(max_length=20, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    
    # Campos derivados del user agent
    device_type = models.CharField(max_length=50, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)
    is_mobile = models.BooleanField(null=True)
    is_tablet = models.BooleanField(null=True)
    is_touch_capable = models.BooleanField(null=True)
    is_pc = models.BooleanField(null=True)
    is_bot = models.BooleanField(null=True)

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _('Registro de actividad')
        verbose_name_plural = _('Registros de actividad')
    @property
    def device_icon(self):
        icons = {
            'mobile': 'bi-phone',
            'tablet': 'bi-tablet',
            'pc': 'bi-pc',
            'bot': 'bi-robot'
        }
        
        if self.is_bot: return icons['bot']
        if self.is_mobile: return icons['mobile']
        if self.is_tablet: return icons['tablet']
        return icons['pc']

    @property
    def location_pin(self):
        if self.loc:
            return f"https://maps.googleapis.com/maps/api/staticmap?center={self.loc}&zoom=10&size=200x100&key=TU_API_KEY"
        return None
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"  
    
class CompanySettings(models.Model):
    logo = ResizedImageField(
        size=[400, 200],  # Tamaño aumentado
        quality=90,
        upload_to='company/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg'])
        ],
        null=True,
        blank=True,
        help_text=_('Preferiblemente PNG con fondo transparente (Recomendado 400x150 px)')
    )
    
    class Meta:
        verbose_name = _('Configuración de la empresa')
        verbose_name_plural = verbose_name

    def __str__(self):
        return "Configuración de la Empresa"