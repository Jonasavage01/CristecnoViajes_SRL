import logging

from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.db import IntegrityError
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .filters import ClienteFilter

from .models import Cliente
from .forms import ClienteForm, ClienteEditForm

logger = logging.getLogger(__name__)


class ClienteDetailView(DetailView):
    model = Cliente
    template_name = "crm/cliente_detail.html"
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteEditForm
    template_name = "partials/crm/cliente_edit_form.html"
    
    def get_success_url(self):
        return reverse_lazy('cliente_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Manejar respuesta AJAX
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cliente actualizado exitosamente',
                'redirect_url': self.get_success_url()
            })
        messages.success(self.request, 'Cliente actualizado exitosamente!')
        return response

    def form_invalid(self, form):
        errors = self._compile_form_errors(form)
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': errors,
                'form_errors': form.errors
            }, status=400)
        return super().form_invalid(form)
    
    def _compile_form_errors(self, form):
        errors = []
        for field, error_list in form.errors.items():
            errors.append({
                'field': field,
                'messages': error_list
            })
        return errors

class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "crm/cliente_confirm_delete.html"
    success_url = reverse_lazy('crm_home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
        except Exception as e:
            logger.error(f'Error eliminando cliente: {str(e)}', exc_info=True)
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'message': 'Error interno al eliminar el cliente'
                }, status=500)
            messages.error(request, 'Error al eliminar el cliente')
            return redirect(self.get_success_url())

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Cliente eliminado correctamente'
            })
        
        messages.success(request, 'Cliente eliminado correctamente')
        return redirect(self.get_success_url())

class CRMView(ListView):
    model = Cliente
    template_name = "crm/crm_home.html"
    context_object_name = 'clientes'
    paginate_by = 15
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            cliente_filter = ClienteFilter(self.request.GET, queryset)
            return cliente_filter.apply_filters()
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.model.objects.none()

    def get(self, request, *args, **kwargs):
        try:
            # Validación de filtros vacíos solo cuando se aplica el formulario
            if 'apply_filters' in request.GET:
                cliente_filter = ClienteFilter(request.GET, self.get_queryset())
                if not cliente_filter.has_active_filters:
                    messages.warning(request, "Por favor ingresa al menos un criterio de filtrado")
                    return redirect('crm_home')

            # Manejo de requests AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                self.template_name = 'partials/crm/clientes_table.html'
            
            return super().get(request, *args, **kwargs)

        except ValidationError as e:
            messages.error(request, str(e))
            self.object_list = self.model.objects.none()
            context = self.get_context_data()
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': ClienteForm(),
            'estados': Cliente.ESTADO_CHOICES,
            'default_date': timezone.now().strftime('%Y-%m-%d'),
            'get_params': self._clean_get_params(),
            'has_filters': ClienteFilter(self.request.GET, self.get_queryset()).has_active_filters
        })
        return context

    def _clean_get_params(self):
        """Limpia los parámetros GET para paginación"""
        params = self.request.GET.copy()
        params.pop('page', None)
        return params.urlencode()

    # Métodos de manejo de POST (se mantienen iguales)
    def _compile_form_errors(self, form):
        errors = []
        for field, field_errors in form.errors.items():
            label = form.fields[field].label
            error_msg = f"{label}: {field_errors[0]}"
            if field == 'documento' and 'El archivo es demasiado grande' in field_errors[0]:
                error_msg = "El documento excede el tamaño máximo permitido (5MB)"
            errors.append(error_msg)
        return errors

    def _render_form_with_errors(self, form):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

    def _parse_integrity_error(self, error):
        error_str = str(error).lower()
        if 'unique constraint' in error_str:
            if 'cedula_pasaporte' in error_str:
                return 'La cédula/pasaporte ya está registrada'
            if 'email' in error_str:
                return 'El correo electrónico ya existe'
        return 'Error de duplicidad en los datos'

    def _handle_success_response(self, is_ajax, cliente_id):
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Cliente creado exitosamente!',
                'cliente_id': cliente_id
            })
        messages.success(self.request, 'Cliente creado exitosamente!')
        return redirect('crm_home')

    def _handle_form_errors(self, form, is_ajax):
        errors = self._compile_form_errors(form)
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': errors,
                'form_errors': form.errors
            }, status=400)
        messages.error(self.request, 'Por favor corrija los errores en el formulario')
        return self._render_form_with_errors(form)

    def _handle_integrity_error(self, error, is_ajax):
        error_message = self._parse_integrity_error(error)
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': [error_message],
                'error_type': 'integrity_error'
            }, status=409)
        messages.error(self.request, error_message)
        return redirect('crm_home')

    def _handle_generic_error(self, error, is_ajax):
        error_message = f'Error del servidor: {str(error)}'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': [error_message],
                'error_type': 'server_error'
            }, status=500)
        messages.error(self.request, error_message)
        return redirect('crm_home')

    def post(self, request, *args, **kwargs):
        form = ClienteForm(request.POST, request.FILES)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            if form.is_valid():
                cliente = form.save()
                logger.info(f'Cliente creado: {cliente.id}')
                return self._handle_success_response(is_ajax, cliente.id)
            
            logger.warning('Errores de validación en el formulario')
            return self._handle_form_errors(form, is_ajax)
            
        except IntegrityError as e:
            logger.error(f'Error de integridad: {str(e)}')
            return self._handle_integrity_error(e, is_ajax)
            
        except Exception as e:
            logger.critical(f'Error inesperado: {str(e)}', exc_info=True)
            return self._handle_generic_error(e, is_ajax)