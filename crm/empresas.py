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
from django.urls import reverse
from django.template.loader import render_to_string 

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
            queryset = Empresa.objects.prefetch_related('documentos_empresa')
            empresa_filter = EmpresaFilter(self.request.GET, queryset)
            return empresa_filter.apply_filters().order_by('-fecha_registro')
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.model.objects.none()

        # Modificar el método get para mejor manejo de AJAX
    def get(self, request, *args, **kwargs):
        try:
        # Inicializar el queryset base
            self.object_list = self.get_queryset()
        
            if 'apply_filters' in request.GET:
                empresa_filter = EmpresaFilter(request.GET, self.object_list)
            
                if not empresa_filter.has_active_filters:
                    messages.warning(request, "Por favor ingresa al menos un criterio de filtrado")
                    return redirect('empresas')
            
            # Aplicar filtros y actualizar object_list
                self.object_list = empresa_filter.apply_filters()
        
        # Manejar requests AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                self.template_name = 'partials/crm/empresas_table.html'
                context = self.get_context_data()
                return self.render_to_response(context)
        
        # Llamar al get() de la clase base con el object_list actualizado
            return super().get(request, *args, **kwargs)
    
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('empresas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': EmpresaForm(),
            'estados': Empresa.ESTADO_CHOICES,
            'default_date': timezone.now().strftime('%Y-%m-%d'),
            'has_filters': EmpresaFilter(self.request.GET, self.get_queryset()).has_active_filters,
            'filter_params': self._clean_get_params()
            
        })
        return context

    def _clean_get_params(self):  # <-- Añadir este método
        """Limpia los parámetros GET eliminando 'page' para mantener los filtros en la paginación"""
        params = self.request.GET.copy()
        if 'page' in params:
            del params['page']
        return params.urlencode()

    
    def _handle_success_response(self, is_ajax, empresa_id):
        if is_ajax:
            empresa = Empresa.objects.get(pk=empresa_id)
            
            # Renderizar tabla actualizada
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            table_html = render_to_string('partials/crm/empresas_table.html', context, self.request)
            
            return JsonResponse({
                'success': True,
                'message': 'Empresa creada exitosamente!',
                'table_html': table_html,  # Clave crítica para actualización
                'empresa_data': {
                    'id': empresa.id,
                    'nombre_comercial': empresa.nombre_comercial,
                    'rnc': empresa.rnc,
                    'estado': empresa.get_estado_display(),
                    'fecha_registro': empresa.fecha_registro.strftime('%d/%m/%Y'),
                    'telefono': empresa.telefono,
                    'direccion_electronica': empresa.direccion_electronica,
                    'representante': empresa.representante,
                    'edit_url': reverse('empresa_edit', args=[empresa_id]),
                }
            })
        
        messages.success(self.request, 'Empresa creada exitosamente!')
        return redirect('empresas')

    def _handle_form_errors(self, form, is_ajax):
        # Reemplazar la línea errors = self._compile_form_errors(form) por:
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{form.fields[field].label}: {error}")
    
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': errors,
                'form_errors': form.errors
            }, status=400)
    
    # Para requests normales, necesitamos re-renderizar el template con el formulario
        messages.error(self.request, 'Por favor corrija los errores en el formulario')
        context = self.get_context_data()
        context['form'] = form  # Pasar el formulario con errores
        return self.render_to_response(context)

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
        """Pasar el usuario actual y la instancia al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        # Asegurar que la instancia está correctamente asignada
        if not kwargs.get('instance'):
            kwargs['instance'] = self.get_object()
        return kwargs

    def post(self, request, *args, **kwargs):
        """Override para asegurar la instancia antes de procesar el formulario"""
        self.object = self.get_object()
        logger.debug(f"Editando empresa PK: {self.object.pk}")
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
        """Manejar errores de unicidad específicos"""
        if 'rnc' in form.errors:
            logger.warning(f"Intento de RNC duplicado: {form.data.get('rnc')}")
        if 'direccion_electronica' in form.errors:
            logger.warning(f"Intento de email duplicado: {form.data.get('direccion_electronica')}")
        
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
    
