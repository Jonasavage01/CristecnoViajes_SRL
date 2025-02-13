from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.db import IntegrityError
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import ListView
from django.db import IntegrityError
from django.utils import timezone
from .models import Cliente
from .forms import ClienteForm


from .models import Cliente
from .forms import ClienteForm

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
    form_class = ClienteForm
    template_name = "crm/cliente_form.html"
    success_url = reverse_lazy('crm_home')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado exitosamente!')
        return super().form_valid(form)

class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "crm/cliente_confirm_delete.html"
    success_url = reverse_lazy('crm_home')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cliente eliminado correctamente')
        return super().delete(request, *args, **kwargs)

class CRMView(ListView):
    model = Cliente
    template_name = "crm/crm_home.html"
    context_object_name = 'clientes'
    paginate_by = 15
    ordering = ['-fecha_creacion']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClienteForm()
        context['estados'] = Cliente.ESTADO_CHOICES
        context['default_date'] = timezone.now().strftime('%Y-%m-%d')
        return context

    def post(self, request, *args, **kwargs):
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                cliente = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Cliente creado exitosamente!',
                    'cliente_id': cliente.id
                })
            except IntegrityError as e:
                error_message = self._handle_integrity_error(e)
                return JsonResponse({
                    'success': False,
                    'errors': [error_message]
                }, status=400)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'errors': [f'Error inesperado: {str(e)}']
                }, status=500)
        else:
            errors = self._compile_form_errors(form)
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)

    def _handle_integrity_error(self, error):
        error_str = str(error).lower()
        if 'cedula_pasaporte' in error_str:
            return 'La cédula/pasaporte ya está registrada'
        if 'email' in error_str:
            return 'El correo electrónico ya existe'
        return 'Error de integridad en la base de datos'

    def _compile_form_errors(self, form):
        errors = []
        for field, field_errors in form.errors.items():
            label = form.fields[field].label
            error_msg = f"{label}: {field_errors[0]}"
            
            # Manejo especial para errores de archivo
            if field == 'documento' and 'El archivo es demasiado grande' in field_errors[0]:
                error_msg = "El documento excede el tamaño máximo permitido (5MB)"
            
            errors.append(error_msg)
        return errors

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClienteForm()
        context['estados'] = Cliente.ESTADO_CHOICES
        context['default_date'] = timezone.now().strftime('%Y-%m-%d')
        return context

    def post(self, request, *args, **kwargs):
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cliente creado exitosamente!')
                return redirect('crm_home')
            except IntegrityError as e:
                error_message = 'Error: '
                if 'cedula_pasaporte' in str(e):
                    error_message += 'La cédula/pasaporte ya existe'
                elif 'email' in str(e):
                    error_message += 'El correo electrónico ya está registrado'
                else:
                    error_message += 'Error al guardar el cliente'
                messages.error(request, error_message)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)