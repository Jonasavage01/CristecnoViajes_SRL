# crm/views/cliente_page.py
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import Cliente
from .forms import ClienteEditForm
import logging
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

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
            'Sistema': 'gear'
        }
        
        context['secciones'] = [
            {
                'titulo': 'Datos Personales',
                'icono': icon_map['Datos Personales'],
                'campos': [
                    ('Cédula/Pasaporte', cliente.cedula_pasaporte),
                    ('Fecha Nacimiento', cliente.fecha_nacimiento.strftime("%d/%m/%Y")),
                    ('Edad', cliente.get_edad()),
                    ('Nacionalidad', cliente.nacionalidad.name),
                ]
            },
            {
                'titulo': 'Contacto',
                'icono': icon_map['Contacto'],
                'campos': [
                    ('Teléfono', cliente.telefono),
                    ('Móvil', cliente.movil),
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
        
        return context

class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteEditForm
    template_name = "partials/crm/cliente_edit_form.html"
    
    def get_success_url(self):
        return reverse_lazy('cliente_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cliente actualizado exitosamente',
                'new_data': {
                    'nombre_apellido': self.object.nombre_apellido,
                    'estado': self.object.get_estado_display(),
                    'estado_color': self.object.get_estado_color(),
                    'ultima_actividad': self.object.ultima_actividad.strftime("%d/%m/%Y %H:%M")
                }
            })
        return response
    
# Agregar después de ClienteUpdateView
class DocumentUploadView(View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        file = request.FILES.get('documento')
        
        if file:
            # Validar tipo de archivo
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if file.content_type not in allowed_types:
                return JsonResponse({'success': False, 'error': 'Tipo de archivo no permitido'}, status=400)
            
            # Validar tamaño (max 5MB)
            if file.size > 5 * 1024 * 1024:
                return JsonResponse({'success': False, 'error': 'El archivo excede 5MB'}, status=400)
            
            cliente.documento = file
            cliente.save()
            return JsonResponse({
                'success': True,
                'document_url': cliente.documento.url,
                'filename': cliente.documento.name.split('/')[-1]
            })
        return JsonResponse({'success': False, 'error': 'No se recibió ningún archivo'}, status=400)

class NotesUpdateView(View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        notas = request.POST.get('notas', '')
        
        cliente.notas = notas
        cliente.save()
        return JsonResponse({
            'success': True,
            'updated_at': cliente.ultima_actividad.strftime("%d/%m/%Y %H:%M")
        })