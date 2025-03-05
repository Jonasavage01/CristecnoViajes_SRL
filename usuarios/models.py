from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

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
    must_change_password = models.BooleanField(
        _('Debe cambiar contraseña'),
        default=False,
        help_text=_('Forzar cambio de contraseña en próximo inicio de sesión')
    )
    
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

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _('Registro de actividad')
        verbose_name_plural = _('Registros de actividad')

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"  # ti