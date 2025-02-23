# Standard library imports
import os
import uuid
import logging

# Django URL imports
from django.urls import reverse_lazy


# Django utilities
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.utils.decorators import method_decorator

# Django HTTP and exceptions
from django.http import JsonResponse
from django.core.exceptions import ValidationError

# Django authentication and messages
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# Django shortcuts
from django.shortcuts import get_object_or_404, redirect

# Django class-based views
from django.views.generic import (
    View,
    DetailView,
    UpdateView,
    FormView,
    DeleteView
)

# Project-specific imports: Models
from .models import Cliente, DocumentoCliente, NotaCliente

# Project-specific imports: Forms
from .forms import ClienteEditForm, DocumentoForm


logger = logging.getLogger(__name__)

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