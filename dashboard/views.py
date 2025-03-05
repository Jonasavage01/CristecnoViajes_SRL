from django.views.generic import TemplateView
from crm.mixins import AuthRequiredMixin

from django.utils import timezone
from crm.models import Cliente  # Ajustar según tus modelos

class DashboardView(AuthRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    allowed_roles = ['admin', 'clientes', 'contabilidad', 'reservas']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Estadísticas básicas
        stats = {
            'total_clientes': Cliente.objects.count(),
            'clientes_activos': Cliente.objects.filter(estado='activo').count(),
            'ultimo_acceso': user.last_login.strftime("%d/%m/%Y %H:%M") if user.last_login else "Nunca"
        }

        context.update({
            'page_title': 'Panel Principal',
            'user_profile': {
                'nombre': user.get_full_name(),
                'rol': user.get_rol_display(),
                'email': user.email,
                'fecha_registro': user.date_joined.strftime("%d/%m/%Y")
            },
            'stats': stats
        })
        return context