# Standard library imports
import logging
import os
import uuid
from tempfile import NamedTemporaryFile
from django.utils.text import slugify, get_valid_filename
from django.template.loader import render_to_string 

# Django core imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseServerError,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import (
    View,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    FormView,
)

# Third-party package imports
import requests
from weasyprint import HTML

# Project-specific imports: Models
from .models import Cliente, DocumentoCliente, NotaCliente

# Project-specific imports: Forms
from .forms import ClienteForm, ClienteEditForm, DocumentoForm

# Project-specific imports: Filters
from .filters import ClienteFilter

# Logger configuration
logger = logging.getLogger(__name__)






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
        



class ClienteDetailView(DetailView):
    model = Cliente
    template_name = "crm/cliente_detail.html"
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.object
        
        icon_map = {
            'Datos Personales': 'person-badge',
            'Contacto': 'telephone',
            'Laboral': 'briefcase',
            'Sistema': 'gear',
            'Documentos': 'folder',
            'Notas': 'card-text'
        }
        
        # Secciones principales
        context['secciones'] = [
            {
                'titulo': 'Datos Personales',
                'icono': icon_map['Datos Personales'],
                'campos': [
                    ('Nombre', cliente.nombre),
                    ('Apellido', cliente.apellido),
                    ('Cédula/Pasaporte', cliente.cedula_pasaporte),
                    ('Fecha Nacimiento', cliente.fecha_nacimiento.strftime("%d/%m/%Y") if cliente.fecha_nacimiento else 'N/A'),
                    ('Edad', cliente.get_edad()),
                    ('Nacionalidad', cliente.nacionalidad.name),
                ]
            },
            {
                'titulo': 'Contacto',
                'icono': icon_map['Contacto'],
                'campos': [
                    ('Teléfono', cliente.telefono or 'N/A'),
                    ('Móvil', cliente.movil or 'N/A'),
                    ('Email', cliente.email),
                    ('Dirección', cliente.direccion_fisica),
                ]
            },
            {
                'titulo': 'Laboral',
                'icono': icon_map['Laboral'],
                'campos': [
                    ('Lugar de Trabajo', cliente.lugar_trabajo or 'N/A'),
                    ('Cargo', cliente.cargo or 'N/A'),
                ]
            },
            {
                'titulo': 'Sistema',
                'icono': icon_map['Sistema'],
                'campos': [
                    ('Estado', cliente.get_estado_display()),
                    ('Fecha Creación', cliente.fecha_creacion.strftime("%d/%m/%Y %H:%M")),
                    ('Última Actividad', cliente.ultima_actividad.strftime("%d/%m/%Y %H:%M")),
                ]
            }
        ]
        
        # Documentos adjuntos
        context['documentos_json'] = [
    {
        'url': doc.archivo.url,
        'name': doc.nombre_archivo,
        'type': doc.extension,
        'upload_date': doc.fecha_subida.strftime("%d/%m/%Y %H:%M"),
        'id': doc.id,
        'tipo': doc.tipo  # Cambiar de tipo_display a tipo
    } 
    for doc in self.object.documentos.all().select_related('cliente')
]

        
        # Notas
        context['notas_info'] = {
    'titulo': 'Notas',
    'icono': icon_map['Notas'],
    'contenido': cliente.notas_cliente.all().order_by('-fecha_creacion')
                 .select_related('autor').only('contenido', 'fecha_creacion', 'autor__username'),
    'ultima_actualizacion': cliente.ultima_actividad.strftime("%d/%m/%Y %H:%M")
}
        
        return context


@method_decorator(xframe_options_sameorigin, name='dispatch')
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteEditForm
    template_name = "partials/crm/cliente_edit_form.html"
    
    def get_success_url(self):
        return reverse_lazy('cliente_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Añadir contexto adicional para depuración"""
        context = super().get_context_data(**kwargs)
        context['debug_instance_pk'] = self.object.pk if self.object else 'None'
        return context

    def post(self, request, *args, **kwargs):
        """Override para asegurar la instancia antes de procesar el formulario"""
        logger.debug(f"Editando cliente - Método POST - Usuario: {request.user}")
        self.object = self.get_object()
        logger.debug(f"Instancia obtenida - PK: {self.object.pk}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Manejar respuesta exitosa con depuración"""
        logger.debug("Iniciando form_valid...")
        
        # Guardar cambios
        self.object = form.save()
        logger.info(f"Cliente {self.object.pk} actualizado por {self.request.user}")

        # Respuesta AJAX
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            logger.debug("Respondiendo a solicitud AJAX")
            return JsonResponse({
                'success': True,
                'message': 'Cliente actualizado exitosamente',
                'cliente_data': {
                    'id': self.object.id,
                   'nombre': self.object.nombre,
                    'apellido': self.object.apellido,
            'estado': self.object.estado,
            'estado_display': self.object.get_estado_display(),
           'estado_color': self.object.get_estado_color(),
                    'telefono': self.object.telefono,
                    'email': self.object.email,
                    'cedula': self.object.cedula_pasaporte,
                    'fecha_creacion': self.object.fecha_creacion.strftime("%d/%m/%Y %H:%M")
                }
            })
        
        # Respuesta normal
        messages.success(self.request, 'Cliente actualizado exitosamente!')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """Manejar errores de validación con logging detallado"""
        logger.error("Errores de validación en el formulario de edición")
        logger.debug("Datos del formulario inválidos: %s", form.data)
        logger.debug("Errores detallados: %s", form.errors.as_json())
        
        # Depuración de la instancia
        if hasattr(form, 'instance'):
            logger.debug(f"Instancia en formulario inválido - PK: {form.instance.pk if form.instance else 'None'}")
        else:
            logger.warning("Formulario no tiene instancia asociada")

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


class DocumentUploadView(FormView):
    form_class = DocumentoForm
    template_name = 'clientes/documentos_form.html'
    
    def form_valid(self, form):
        cliente = Cliente.objects.get(pk=self.kwargs['pk'])
        documento = form.save(commit=False)
        documento.cliente = cliente
        
        # Solo asignar usuario si está autenticado
        if self.request.user.is_authenticated:
            documento.subido_por = self.request.user
            
        documento.save()
        
        cliente.ultima_actividad = timezone.now()
        cliente.save()

        return JsonResponse({
           
        'success': True,
        'document': {
            'url': documento.archivo.url,
            'name': documento.nombre_archivo,
            'type': documento.extension,
            'upload_date': documento.fecha_subida.strftime("%d/%m/%Y %H:%M"),
            'id': documento.id,
            'tipo': documento.tipo  # Mantener consistencia con el formato
            }
        })
    
    def form_invalid(self, form):
        logger.error(f"Errores en DocumentUploadView: {form.errors.as_json()}")
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data()
        }, status=400)
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = DocumentoCliente()
        return kwargs

class NotesUpdateView(View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        notas = request.POST.get('notas', '').strip()
        
        if len(notas) > 1000:
            return JsonResponse({
                'success': False, 
                'error': 'Máximo 1000 caracteres'
            }, status=400)
        
        cliente.notas = notas
        cliente.ultima_actividad = timezone.now()
        cliente.save()
        
        return JsonResponse({
            'success': True,
            'updated_at': cliente.ultima_actividad.strftime("%d/%m/%Y %H:%M"),
            'notas_content': notas or 'No hay notas registradas'
        })

class NoteCreateView(View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        contenido = request.POST.get('contenido', '').strip()
        
        if len(contenido) > 1000:
            return JsonResponse({'success': False, 'error': 'Máximo 1000 caracteres'}, status=400)
        
        try:
            # Asegúrate de que el campo 'autor' sea opcional en el modelo o maneja usuarios anónimos
            nota = NotaCliente.objects.create(
                cliente=cliente,
                contenido=contenido,
                autor=request.user if request.user.is_authenticated else None
            )
            cliente.ultima_actividad = timezone.now()
            cliente.save()
            
            return JsonResponse({
    'success': True,
    'nota': {
        'id': nota.id,
        'contenido': nota.contenido,
        'fecha_creacion': nota.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
        'autor': nota.autor.username if nota.autor else 'Sistema'
    }
})
            
        except Exception as e:
            logger.error(f"Error creando nota: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': 'Error del servidor'}, status=500)

class DeleteNoteView(View):
    def delete(self, request, cliente_pk, note_pk):  # Cambiar nombres de parámetros
        try:
            note = NotaCliente.objects.get(id=note_pk, cliente_id=cliente_pk)
            note.delete()
            return JsonResponse({'success': True})
        except NotaCliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Nota no encontrada'}, status=404)

class DocumentDeleteView(DeleteView):
    model = DocumentoCliente
    
    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return JsonResponse({'success': True})
    

class ClientePDFView(DetailView):
    model = Cliente
    template_name = 'crm/cliente_pdf.html'
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.object
        
        try:
            # Optimizar consulta (corregir select_related)
            notas = cliente.notas_cliente.all().order_by('-fecha_creacion').select_related('autor').only(
                'contenido', 'fecha_creacion', 'autor__username'
            )

            context['secciones'] = [
                {
                    'titulo': 'Datos Personales',
                    'campos': [
                        ('Nombre', cliente.nombre),
                        ('Apellido', cliente.apellido),
                        ('Cédula/Pasaporte', cliente.cedula_pasaporte),
                        ('Fecha Nacimiento', cliente.fecha_nacimiento.strftime("%d/%m/%Y") if cliente.fecha_nacimiento else 'N/A'),
                        ('Edad', cliente.get_edad()),
                        ('Nacionalidad', cliente.nacionalidad.name if cliente.nacionalidad else 'N/A'),
                    ]
                },
                {
                    'titulo': 'Contacto',
                    'campos': [
                        ('Teléfono', cliente.telefono or 'N/A'),
                        ('Móvil', cliente.movil or 'N/A'),
                        ('Email', cliente.email or 'N/A'),
                        ('Dirección', cliente.direccion_fisica or 'N/A'),
                    ]
                },
                {
                    'titulo': 'Laboral',
                    'campos': [
                        ('Lugar de Trabajo', cliente.lugar_trabajo or 'N/A'),
                        ('Cargo', cliente.cargo or 'N/A'),
                    ]
                },
                {
                    'titulo': 'Sistema',
                    'campos': [
                        ('Estado', cliente.get_estado_display()),
                        ('Fecha Creación', cliente.fecha_creacion.strftime("%d/%m/%Y %H:%M")),
                        ('Última Actividad', cliente.ultima_actividad.strftime("%d/%m/%Y %H:%M") if cliente.ultima_actividad else 'N/A'),
                    ]
                }
            ]
            
            context['notas'] = notas
            context['generation_date'] = timezone.now().strftime("%d/%m/%Y %H:%M")
            return context

        except Exception as e:
            logger.error(f"Error generando contexto PDF: {str(e)}", exc_info=True)
            raise

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            context = self.get_context_data()
            
            # Renderizar HTML (ya con el import agregado)
            html_string = render_to_string(self.template_name, context)
            
            # Configurar WeasyPrint
            html = HTML(
                string=html_string,
                base_url=request.build_absolute_uri('/'),
                encoding='utf-8'
            )
            
            # Generar PDF
            pdf_file = html.write_pdf(timeout=30)
            
            # Nombre del archivo
            nombre_slug = slugify(f"{self.object.nombre} {self.object.apellido}")
            filename = f"Cliente_{self.object.pk}_{nombre_slug}.pdf"
            
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}", exc_info=True)
            return HttpResponseServerError("Error generando el documento. Por favor intente más tarde.")