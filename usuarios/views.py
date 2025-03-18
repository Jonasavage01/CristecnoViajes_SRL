from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView, ListView, CreateView
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
import logging
from django.views.generic import ListView, DetailView
from .models import UserActivityLog
from django.utils import timezone
from .models import UsuarioPersonalizado, UserActivityLog
from .forms import LoginForm, UserCreationForm, AdminPasswordChangeForm
from crm.mixins import AuthRequiredMixin
from django.views.generic import DetailView
logger = logging.getLogger(__name__)
from django.shortcuts import render
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Q
from django.contrib.auth.models import User
from .models import UsuarioPersonalizado, UserActivityLog
from django.db.models import Prefetch
from django.db.models import OuterRef, Subquery, Exists
from django.db.models import F
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.mixins import RoleAccessMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import CompanySettings
from .forms import CompanySettingsForm
from django.views.generic import UpdateView

def online_users_list(request):
    online_users = UsuarioPersonalizado.objects.filter(
        last_seen__gte=timezone.now() - timezone.timedelta(minutes=2)
    ).annotate(
        last_login_time=Subquery(
            UserActivityLog.objects.filter(
                user=OuterRef('id'),
                activity_type=UserActivityLog.ActivityType.LOGIN
            ).order_by('-timestamp').values('timestamp')[:1]
        )
    ).prefetch_related(
        Prefetch(
            'useractivitylog_set',
            queryset=UserActivityLog.objects.order_by('-timestamp'),
            to_attr='prefetched_activities'
        )
    ).order_by('-last_seen')

    context = {
        'users': online_users,
        'online_count': online_users.count()
    }
    return render(request, 'usuarios/online_users_list.html', context)

# ConfigPanelView actualizado
class ConfigPanelView(TemplateView):
    template_name = 'usuarios/config_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        online_users = UsuarioPersonalizado.objects.filter(
            last_seen__gte=timezone.now() - timezone.timedelta(minutes=2)
        ).order_by('-last_seen')
        
        users = UsuarioPersonalizado.objects.all()
        
        context.update({
            'online_count': online_users.count(),
            'online_users_list': online_users[:5],
            'total_users': users.count(),
            'active_accounts': users.filter(is_active=True).count(),
            'inactive_accounts': users.filter(is_active=False).count(),
            'activity_logs': UserActivityLog.objects.all().order_by('-timestamp')[:10],
            'page_title': _('Panel de Configuración'),
            'current_user': self.request.user
        })
        
        return context

# Vista activity_ping
@require_http_methods(["POST"])
def activity_ping(request):
    if request.user.is_authenticated:
        return JsonResponse({'status': 'active'})
    return JsonResponse({'status': 'inactive'}, status=401)

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    extra_context = {
        'page_title': _('Acceso al Sistema'),
        'help_text': _('Ingrese sus credenciales para acceder al panel de administración')
    }

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f'Intento de acceso desde {request.META.get("REMOTE_ADDR")}')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        
    
        
        # Actualizar última sesión
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Resetear intentos fallidos
        if hasattr(user, 'login_attempts'):
            user.login_attempts = 0
            user.save()
        
        # Prevención de fixation de sesión
        self.request.session.cycle_key()
        
        # Seguridad adicional de headers
        response = super().form_valid(form)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response

    def form_invalid(self, form):
    # Registrar intento fallido
        username = form.data.get('username', '')
        try:
            user = UsuarioPersonalizado.objects.get(username=username)
        # Usar getattr para evitar KeyError
            user.login_attempts = getattr(user, 'login_attempts', 0) + 1
            user.save(update_fields=['login_attempts'])
        
            if user.login_attempts >= 3:
                logger.warning(f'Bloqueo temporal para usuario {username} - Demasiados intentos fallidos')
                messages.error(
                    self.request,
                 _('Cuenta temporalmente bloqueada por demasiados intentos fallidos')
                )
            
        except UsuarioPersonalizado.DoesNotExist:
            logger.warning(f'Intento de acceso con usuario inexistente: {username}')
            pass
        
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    http_method_names = ['post']

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Actualizar last_seen al hacer logout
            user = request.user
            user.last_seen = timezone.now()
            user.save(update_fields=['last_seen'])
            
            # Registrar actividad de logout
            

        response = super().dispatch(request, *args, **kwargs)
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        return response


class UserListView(RoleAccessMixin, ListView):
    model = UsuarioPersonalizado
    template_name = 'usuarios/user_list.html'
    context_object_name = 'users'
    allowed_roles = ['admin']
    paginate_by = 20
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        search = self.request.GET.get('q')
        queryset = super().get_queryset()
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['page_title'] = _('Gestión de Usuarios')
        return context

class UserCreateView(RoleAccessMixin, CreateView):
    model = UsuarioPersonalizado
    form_class = UserCreationForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('user_list')
    allowed_roles = ['admin']
    
    def form_valid(self, form):
        form.instance._created_by = self.request.user 
        response = super().form_valid(form)
        success_message = _('Usuario %(username)s creado exitosamente') % {'username': self.object.username}
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': success_message,
                'redirect_url': self.get_success_url()
            })
        
        messages.success(self.request, success_message)
        logger.info(f'Usuario {self.object.username} creado por {self.request.user}')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': [str(error) for field in form.errors.values() for error in field]
            }, status=400)
            
        messages.error(self.request, _('Error al crear el usuario'))
        return response

class AdminPasswordChangeView(RoleAccessMixin, PasswordChangeView):
    form_class = AdminPasswordChangeForm
    template_name = 'usuarios/admin_password_change.html'
    success_url = reverse_lazy('user_list')
    allowed_roles = ['admin']
    
    def get_object(self):
        return UsuarioPersonalizado.objects.get(pk=self.kwargs['pk'])
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.get_object()
        success_message = _('Contraseña actualizada para el usuario %(username)s') % {'username': user.username}
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': success_message,
                'redirect_url': self.get_success_url()
            })
        
        messages.success(self.request, success_message)
        logger.info(f'Contraseña cambiada para {user.username} por {self.request.user}')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': [str(error) for field in form.errors.values() for error in field]
            }, status=400)
            
        messages.error(self.request, _('Error al cambiar la contraseña'))
        return response

class ActivityLogDetailView(RoleAccessMixin, DetailView):
    model = UserActivityLog
    template_name = 'usuarios/activity_detail.html'
    allowed_roles = ['admin']
    context_object_name = 'log'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log = self.object

        # Procesamiento de coordenadas
        lat, lon = None, None
        if log.loc:
            try:
                # Limpieza y validación estricta
                parts = log.loc.strip().split(',')
                if len(parts) == 2:
                    lat = float(parts[0])
                    lon = float(parts[1])
            except (ValueError, TypeError) as e:
                logger.warning(f"Formato inválido de coordenadas: {log.loc}", exc_info=True)

        # Construcción de ubicación
        location = []
        if log.city: location.append(log.city)
        if log.region: location.append(log.region)
        if log.country: location.append(log.country)
        location_str = ', '.join(location) if location else None

        # Contexto mejorado
        context.update({
            'latitude': lat,
            'longitude': lon,
            'map_url': f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else None,
            'location_str': location_str,
            'has_geo_data': any([lat, lon, location_str]),
            'is_local_ip': log.ip_address == '127.0.0.1',
            'geo_data_available': any([log.city, log.region, log.country, log.loc])
        })
        return context

class ActivityLogView(RoleAccessMixin, ListView):
    model = UserActivityLog
    template_name = 'usuarios/activity_log.html'
    context_object_name = 'logs'
    allowed_roles = ['admin']
    paginate_by = 25
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(ip_address__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Historial de Actividad'),
            'search_query': self.request.GET.get('q', '')
        })
        return context

class CompanySettingsView(RoleAccessMixin,UpdateView):
    model = CompanySettings
    form_class = CompanySettingsForm
    template_name = 'usuarios/customization.html'
    permission_required = 'usuarios.change_companysettings'
    success_url = reverse_lazy('customization')
    allowed_roles = ['admin']
    
    def get_object(self):
        # Obtener o crear la instancia única
        obj, created = CompanySettings.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        messages.success(self.request, _('¡Logo actualizado correctamente!'))
        return super().form_valid(form)