from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class AuthRequiredMixin(LoginRequiredMixin):
    login_url = '/usuarios/login/'
    allowed_roles = ['admin']
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if (request.user.rol not in self.allowed_roles 
            and not request.user.is_superuser
            and not request.user.is_staff):
            raise PermissionDenied("No tiene permisos para acceder a esta sección")
            
        return super().dispatch(request, *args, **kwargs)