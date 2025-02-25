# empresas.py
from django.views.generic import ListView
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.http import JsonResponse
import logging
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.forms.models import model_to_dict

from .models import Empresa
from .empresas_forms import EmpresaForm  # Asegúrate de crear este formulario
from .empresas_filters import EmpresaFilter

from .empresas_forms import EmpresaEditForm, DocumentoEmpresaForm

logger = logging.getLogger(__name__)

class EmpresasView(ListView):
    model = Empresa
    template_name = "crm/empresas.html"
    context_object_name = 'empresas'
    paginate_by = 15
    ordering = ['-fecha_registro']

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            empresa_filter = EmpresaFilter(self.request.GET, queryset)
            return empresa_filter.apply_filters()
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.model.objects.none()

    def get(self, request, *args, **kwargs):
        try:
            if 'apply_filters' in request.GET:
                empresa_filter = EmpresaFilter(request.GET, self.get_queryset())
                if not empresa_filter.has_active_filters:
                    messages.warning(request, "Por favor ingresa al menos un criterio de filtrado")
                    return redirect('empresas')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                self.template_name = 'partials/crm/empresas_table.html'
            
            return super().get(request, *args, **kwargs)

        except ValidationError as e:
            messages.error(request, str(e))
            self.object_list = self.model.objects.none()
            context = self.get_context_data()
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': EmpresaForm(),
            'estados': Empresa.ESTADO_CHOICES,
            'default_date': timezone.now().strftime('%Y-%m-%d'),
            'get_params': self._clean_get_params(),
            'has_filters': EmpresaFilter(self.request.GET, self.get_queryset()).has_active_filters
        })
        return context

    def _clean_get_params(self):
        params = self.request.GET.copy()
        params.pop('page', None)
        return params.urlencode()

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
            if 'rnc' in error_str:
                return 'El RNC ya está registrado'
            if 'direccion_electronica' in error_str:
                return 'La dirección electrónica ya existe'
        return 'Error de duplicidad en los datos'

    def _handle_success_response(self, is_ajax, empresa_id):
        if is_ajax:
            return JsonResponse({
    'success': True,
    'message': '...',
    'empresa_id': empresa_id,  # Corregir variable id -> empresa_id
    # Para actualizar tabla incluir:
    'empresa_data': { ... }  # Opcional si se necesita actualizar sin recargar
})
        messages.success(self.request, 'Empresa creada exitosamente!')
        return redirect('empresas')

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
        return redirect('empresas')

    def _handle_generic_error(self, error, is_ajax):
        error_message = f'Error del servidor: {str(error)}'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': [error_message],
                'error_type': 'server_error'
            }, status=500)
        messages.error(self.request, error_message)
        return redirect('empresas')

    def post(self, request, *args, **kwargs):
        form = EmpresaForm(request.POST, request.FILES)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            if form.is_valid():
                empresa = form.save()
                logger.info(f'Empresa creada: {empresa.id}')
                return self._handle_success_response(is_ajax, empresa.id)
            
            logger.warning('Errores de validación en el formulario')
            return self._handle_form_errors(form, is_ajax)
            
        except IntegrityError as e:
            logger.error(f'Error de integridad: {str(e)}')
            return self._handle_integrity_error(e, is_ajax)
            
        except Exception as e:
            logger.critical(f'Error inesperado: {str(e)}', exc_info=True)
            return self._handle_generic_error(e, is_ajax)
        

class EmpresaUpdateView(UpdateView):
    model = Empresa
    form_class = EmpresaEditForm
    template_name = "partials/crm/empresa_edit_form.html"
    
    def get_success_url(self):
        return reverse_lazy('empresa_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Contexto adicional para depuración
        context['debug_instance_pk'] = self.object.pk if self.object else 'None'
        context['documento_form'] = DocumentoEmpresaForm()  # Formulario para documentos
        return context
    def get_queryset(self):
        """Asegurar que solo se puedan editar empresas existentes"""
        return Empresa.objects.all()
    
    def get_form_kwargs(self):
        """Pasar el usuario actual al formulario si es necesario"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        """Override para asegurar la instancia antes de procesar el formulario"""
        logger.debug(f"Editando empresa - Método POST - Usuario: {request.user}")
        self.object = self.get_object()
        logger.debug(f"Instancia obtenida - PK: {self.object.pk}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Manejar respuesta exitosa con depuración"""
        logger.debug("Iniciando form_valid para empresa...")
        
        # Actualizar última actividad
        self.object.ultima_actividad = timezone.now()
        
        # Guardar cambios
        self.object = form.save()
        logger.info(f"Empresa {self.object.pk} actualizada por {self.request.user}")

        # Respuesta AJAX
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            logger.debug("Respondiendo a solicitud AJAX para empresa")
            return JsonResponse({
                'success': True,
                'message': 'Empresa actualizada exitosamente',
                'empresa_data': {
                    'id': self.object.id,
                    'nombre_comercial': self.object.nombre_comercial,
                    'razon_social': self.object.razon_social,
                    'rnc': self.object.rnc,
                    'estado': self.object.estado,
                    'estado_display': self.object.get_estado_display(),
                    'estado_color': self.object.get_estado_color(),
                    'telefono': self.object.telefono,
                    'telefono2': self.object.telefono2,
                    'direccion_electronica': self.object.direccion_electronica,
                    'fecha_registro': self.object.fecha_registro.strftime("%d/%m/%Y %H:%M"),
                    'ultima_actividad': self.object.ultima_actividad.strftime("%d/%m/%Y %H:%M")
                }
            })
        
        # Respuesta normal
        messages.success(self.request, '¡Empresa actualizada exitosamente!')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """Manejar errores de validación con logging detallado"""
        logger.error("Errores de validación en el formulario de edición de empresa")
        logger.debug("Datos del formulario inválidos: %s", form.data)
        logger.debug("Errores detallados: %s", form.errors.as_json())
        
        # Depuración de la instancia
        if hasattr(form, 'instance'):
            logger.debug(f"Instancia en formulario inválido - PK: {form.instance.pk if form.instance else 'None'}")
        else:
            logger.warning("Formulario de empresa no tiene instancia asociada")

        # Respuesta AJAX
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
                'form_errors': form.errors.get_json_data(),
                'debug': {
                    'instance_pk': self.object.pk if self.object else 'None',
                    'form_instance_pk': form.instance.pk if form.instance else 'None'
                }
            }, status=400)
            
        return super().form_invalid(form)

    def _compile_form_errors(self, form):
        """Método auxiliar para formatear errores (usado en plantillas)"""
        errors = []
        for field, error_list in form.errors.items():
            errors.append({
                'field': field,
                'messages': error_list
            })
        return errors
    
