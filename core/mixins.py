# core/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)

class RoleAccessMixin(LoginRequiredMixin):
    """
    Control de acceso basado en roles con registro de actividad
    """
    allowed_roles = None
    permission_denied_message = "Acceso no autorizado"
    raise_exception = True
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if self.allowed_roles is None:
            raise ImproperlyConfigured(
                "Debe definir 'allowed_roles' para usar RoleAccessMixin"
            )
        
        if not self.has_permission():
            self.log_access_attempt(request)
            raise PermissionDenied(self.get_permission_denied_message())
        
        return super().dispatch(request, *args, **kwargs)
    
    def has_permission(self):
        user = self.request.user
        if not hasattr(user, 'rol'):
            logger.error(f"Usuario {user} no tiene atributo 'rol'")
            return False
        return user.is_superuser or (user.rol in self.allowed_roles)
    
    def get_permission_denied_message(self):
        return (
            f"{self.permission_denied_message}. "
            f"Roles permitidos: {', '.join(self.allowed_roles)}"
        )
    
    def log_access_attempt(self, request):
        logger.warning(
            f"Intento de acceso no autorizado: "
            f"Usuario: {request.user.username}, "
            f"Rol: {request.user.rol}, "
            f"URL: {request.path}"  # Corregido request.Path -> request.path
        )