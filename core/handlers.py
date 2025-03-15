from django.views import View
from django.shortcuts import render
from django.utils.translation import gettext as _

class HTTPErrorView(View):
    """Vista base para errores HTTP"""
    template_name = None
    status_code = 400
    
    def get_context_data(self, request, exception=None):
        return {
            'error_code': self.status_code,
            'exception': str(exception) if exception else None,
            'user': request.user,
            'path': request.path,
            'support_email': 'soporte@tudominio.com',
            'support_phone': '+18498625049'
        }
    
    def get(self, request, exception=None, *args, **kwargs):
        context = self.get_context_data(request, exception)
        return render(
            request,
            self.template_name,
            context,
            status=self.status_code
        )

# Vistas específicas para cada error
class HTTP403ForbiddenView(HTTPErrorView):
    template_name = 'core/403.html'
    status_code = 403

# Configuración de handlers
handler403 = HTTP403ForbiddenView.as_view()