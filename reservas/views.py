from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.db.models import Q
from django.core.serializers import serialize
from .models import Reserva
from crm.models import Cliente, Empresa
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from datetime import date
from .models import Hotel, TipoHabitacion,HabitacionReserva
from django.urls import reverse
from .forms import HotelForm, TipoHabitacionFormSet
from django.views.generic import CreateView
from django.urls import reverse_lazy
from core.mixins import RoleAccessMixin
from django.contrib import messages
from django.db import transaction

from django.http import HttpResponseRedirect
from django.views.generic import (
    View,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    FormView,
)


def reservas_home(request): 
    return render(request, 'reservas/reservas_home.html', {
       
    })

class ReservaWizard(TemplateView):

    template_name = 'reservas/wizard/paso_{paso}.html'
    
    def get_template_names(self):
        paso = self.kwargs.get('paso', 1)
        return [self.template_name.format(paso=paso)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today().isoformat()
        paso_actual = self.kwargs.get('paso', 1)
        
        # Contexto adicional para el paso 3
        if paso_actual == 3:
            try:
                reserva = Reserva.objects.get(id=self.request.session['reserva_id'])
                context['habitaciones_existentes'] = reserva.habitaciones.all()
                context['hoteles'] = Hotel.objects.filter(activo=True)
            except:
                context['habitaciones_existentes'] = []
                context['hoteles'] = Hotel.objects.none()

        context.update({
            'paso_actual': paso_actual,
            'total_pasos': 4,
            'tipo_reserva': self.kwargs['tipo']
        })
        return context
    


    def post(self, request, *args, **kwargs):
        paso = self.kwargs.get('paso', 1)
        handler = getattr(self, f'handle_paso{paso}', None)
        
        if not handler:
            return HttpResponseBadRequest("Paso inválido")
            
        try:
            reserva = handler(request)
            request.session['reserva_id'] = reserva.id
            next_paso = paso + 1 if paso < 4 else 4
            
            return JsonResponse({
                'redirect': reverse('reservas:wizard_paso', kwargs={
                    'tipo': self.kwargs['tipo'],
                    'paso': next_paso
                })
            })
        
        except ValidationError as e:
            return JsonResponse({'error': str(e), 'type': 'validation'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error interno: {str(e)}', 'type': 'server'}, status=500)

    def handle_paso1(self, request):
        try:
            cliente_id = request.POST.get('cliente_id')
            empresa_id = request.POST.get('empresa_id')
            
            if not cliente_id and not empresa_id:
                raise ValidationError('Debe seleccionar un cliente o empresa')
                
            reserva = Reserva.objects.create(
                cliente_id=cliente_id,
                empresa_id=empresa_id,
                tipo_reserva=self.kwargs['tipo'],
                creado_por=request.user
            )
            
            return reserva
            
        except Exception as e:
            raise ValidationError(f'Error al crear reserva: {str(e)}')

    def handle_paso2(self, request):
        try:
            reserva = Reserva.objects.get(id=request.session['reserva_id'])
            reserva.fecha_entrada = request.POST['fecha_entrada']
            reserva.fecha_salida = request.POST['fecha_salida']
            
            # Validación adicional
            if reserva.fecha_salida <= reserva.fecha_entrada:
                raise ValidationError('La fecha de salida debe ser posterior')
                
            reserva.adultos = int(request.POST.get('adultos', 1))
            if reserva.adultos < 1:
                raise ValidationError('Debe haber al menos 1 adulto')
                
            reserva.adolescentes = int(request.POST.get('adolescentes', 0))
            reserva.ninos = int(request.POST.get('ninos', 0))
            reserva.infantes = int(request.POST.get('infantes', 0))
            reserva.paso_actual = 3  # Actualizar a paso 3
            reserva.save()
            
            return reserva
            
        except Reserva.DoesNotExist:
            raise ValidationError('Reserva no encontrada en sesión')
    
    def handle_paso3(self, request):
        try:
            reserva = Reserva.objects.get(id=request.session['reserva_id'])
            reserva.habitaciones.all().delete()
        
            hotel_id = request.POST.get('hotel')
            if not hotel_id:
                raise ValidationError({'hotel': 'Seleccione un hotel'})
        
            hotel = Hotel.objects.get(id=hotel_id, activo=True)  # Solo hoteles activos
        
            # Procesar habitaciones usando índices estructurados
            indexes = {k.split('_')[1] for k in request.POST if k.startswith('habitaciones_') and '_tipo' in k}
        
            for index in indexes:
                tipo_id = request.POST.get(f'habitaciones_{index}_tipo')
                cantidad = int(request.POST.get(f'habitaciones_{index}_cantidad', 1))
            
                if not tipo_id or cantidad < 1:
                    continue  # Saltar elementos inválidos
                
                tipo_hab = TipoHabitacion.objects.get(id=tipo_id, hotel=hotel)
                HabitacionReserva.objects.create(
                    reserva=reserva,
                    tipo_habitacion=tipo_hab,
                    cantidad=cantidad
                )
        
            if not reserva.habitaciones.exists():
                raise ValidationError('Debe agregar al menos una habitación')
        
            reserva.paso_actual = 4
            reserva.save()
            return reserva
        
        except Hotel.DoesNotExist:
            raise ValidationError('Hotel no encontrado o inactivo')

class Paso1SeleccionCliente(RoleAccessMixin,ReservaWizard):
    allowed_roles = ['admin', 'reservas']
    step = 1
    
    def post(self, request, *args, **kwargs):
        # Cambiar la respuesta para usar el sistema de wizard
        return super().post(request, *args, **kwargs)
    
    def handle_step(self, request):
        # Mover aquí la lógica de creación de reserva
        cliente_id = request.POST.get('cliente_id')
        empresa_id = request.POST.get('empresa_id')
        
        if not cliente_id and not empresa_id:
            raise ValidationError('Seleccione cliente o empresa')
        
        return Reserva.objects.create(
            cliente_id=cliente_id,
            empresa_id=empresa_id,
            tipo_reserva=self.kwargs['tipo'],
            creado_por=request.user
        )

class Paso2DatosHuespedes(RoleAccessMixin,TemplateView):
    allowed_roles = ['admin', 'reservas']
    template_name = 'reservas/wizard/paso_2.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'today': date.today().isoformat(),
            'paso_actual': 2,
            'total_pasos': 4,
            'tipo_reserva': self.kwargs['tipo']
        })
        return context

    def post(self, request, *args, **kwargs):
        try:
            reserva = Reserva.objects.get(id=request.session['reserva_id'])
            
            # Validar fechas
            fecha_entrada = request.POST['fecha_entrada']
            fecha_salida = request.POST['fecha_salida']
            if fecha_salida <= fecha_entrada:
                raise ValidationError('La fecha de salida debe ser posterior a la entrada')
            
            # Validar huéspedes
            adultos = int(request.POST.get('adultos', 1))
            if adultos < 1:
                raise ValidationError('Debe haber al menos 1 adulto')
            
            # Actualizar reserva
            reserva.fecha_entrada = fecha_entrada
            reserva.fecha_salida = fecha_salida
            reserva.adultos = adultos
            reserva.adolescentes = int(request.POST.get('adolescentes', 0))
            reserva.ninos = int(request.POST.get('ninos', 0))
            reserva.infantes = int(request.POST.get('infantes', 0))
            reserva.paso_actual = 3
            reserva.save()
            
            return redirect('reservas:wizard_paso', tipo=self.kwargs['tipo'], paso=3)
        
        except ValidationError as e:
            return JsonResponse({'error': str(e), 'type': 'validation'}, status=400)
        except Reserva.DoesNotExist:
            return JsonResponse({'error': 'Reserva no encontrada', 'type': 'session'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error interno del servidor', 'type': 'server'}, status=500)

class BuscarClientesEmpresasView(RoleAccessMixin,View):
    allowed_roles = ['admin', 'reservas']
    def get(self, request, *args, **kwargs):
        search_term = request.GET.get('q', '')
        
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=search_term) |
            Q(apellido__icontains=search_term) |
            Q(cedula_pasaporte__icontains=search_term)
        )[:5]
        
        empresas = Empresa.objects.filter(
            Q(nombre_comercial__icontains=search_term) |
            Q(rnc__icontains=search_term)
        )[:5]
        
        resultados = {
            'clientes': [
                {
                    'id': c.id,
                    'nombre': f'{c.nombre} {c.apellido}',
                    'identificacion': c.cedula_pasaporte,
                    'tipo': 'cliente'
                } for c in clientes
            ],
            'empresas': [
                {
                    'id': e.id,
                    'nombre': e.nombre_comercial,
                    'identificacion': e.rnc,
                    'tipo': 'empresa'
                } for e in empresas
            ]
        }
        return JsonResponse(resultados)
        
class LimpiarSeleccionView(RoleAccessMixin,View):
    allowed_roles = ['admin', 'reservas']
    def post(self, request, *args, **kwargs):
        if 'reserva_data' in request.session:
            del request.session['reserva_data']
        return JsonResponse({'success': True})

class Paso3SeleccionHotel(TemplateView):
    template_name = 'reservas/wizard/paso_3.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            reserva = Reserva.objects.get(id=self.request.session['reserva_id'])
            habitaciones_existentes = HabitacionReserva.objects.filter(reserva=reserva)
        except:
            habitaciones_existentes = []
        
        context.update({
            'hoteles': Hotel.objects.filter(activo=True),
            'habitaciones_existentes': habitaciones_existentes,
            'paso_actual': 3,
            'total_pasos': 4,
            'tipo_reserva': self.kwargs['tipo']
        })
        return context

    def post(self, request, *args, **kwargs):
        try:
            reserva = Reserva.objects.get(id=request.session['reserva_id'])
            reserva.habitaciones.all().delete()  # Limpiar habitaciones anteriores
            
            hotel_id = request.POST.get('hotel')
            if not hotel_id:
                raise ValidationError('Debe seleccionar un hotel')
            
            hotel = Hotel.objects.get(id=hotel_id)
            habitaciones = []
            
            # Procesar habitaciones
            for key, value in request.POST.items():
                if key.startswith('habitaciones'):
                    parts = key.split('_')
                    if len(parts) == 3 and parts[2] == 'tipo':
                        index = parts[1]
                        tipo_id = value
                        cantidad = request.POST.get(f'habitaciones_{index}_cantidad', 1)
                        
                        if tipo_id and cantidad:
                            try:
                                tipo = TipoHabitacion.objects.get(id=tipo_id, hotel=hotel)
                                HabitacionReserva.objects.create(
                                    reserva=reserva,
                                    tipo_habitacion=tipo,
                                    cantidad=cantidad
                                )
                            except TipoHabitacion.DoesNotExist:
                                raise ValidationError(f'Tipo de habitación inválido para el hotel seleccionado')
            
            if reserva.habitaciones.count() == 0:
                raise ValidationError('Debe agregar al menos una habitación')
            
            reserva.paso_actual = 4
            reserva.save()
            
            return redirect('reservas:wizard_paso', tipo=self.kwargs['tipo'], paso=4)
            
        except ValidationError as e:
            return JsonResponse({'error': str(e), 'type': 'validation'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error: {str(e)}', 'type': 'server'}, status=500)
 
class HotelHabitacionesView(RoleAccessMixin,View):
    allowed_roles = ['admin', 'reservas']
    def get(self, request, hotel_id):
        habitaciones = TipoHabitacion.objects.filter(
            hotel_id=hotel_id,
            hotel__activo=True
        ).values('id', 'nombre', 'capacidad')
        return JsonResponse(list(habitaciones), safe=False)
 
class HotelSearchView(View):
    allowed_roles = ['admin', 'reservas']
    def get(self, request):
        term = request.GET.get('q', '')
        hoteles = Hotel.objects.filter(
            Q(nombre__icontains=term) | 
            Q(ubicacion__icontains=term)
        )[:10]
        
        results = [{
            'id': h.id,
            'text': f"{h.nombre} ({h.ubicacion}) - {h.estrellas}★"
        } for h in hoteles]
        
        return JsonResponse({'results': results})

class HotelCreateView(RoleAccessMixin, CreateView):
    allowed_roles = ['admin', 'reservas']
    model = Hotel
    form_class = HotelForm
    template_name = 'reservas/hotel_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TipoHabitacionFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = TipoHabitacionFormSet(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('reservas:hotel_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        try:
            context = self.get_context_data(form=form)
            formset = context['formset']
            
            with transaction.atomic():
                # Guardar el hotel primero
                self.object = form.save()
                
                # Reinstanciar el formset con la instancia guardada
                formset = TipoHabitacionFormSet(
                    self.request.POST,
                    instance=self.object
                )
                
                if formset.is_valid():
                    formset.save()
                    messages.success(self.request, 'Hotel creado exitosamente')
                    return HttpResponseRedirect(self.get_success_url())
                else:
                    raise forms.ValidationError("Errores en tipos de habitación")
                    
        except Exception as e:
            messages.error(self.request, 'Por favor corrige los errores en los tipos de habitación')
            context['formset'] = formset
            return self.render_to_response(context)
        
    

class HotelUpdateView(RoleAccessMixin, UpdateView):
    allowed_roles = ['admin', 'reservas']
    model = Hotel
    form_class = HotelForm
    template_name = 'reservas/hotel_form.html'
    
    def get_success_url(self):
        return reverse('reservas:hotel_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TipoHabitacionFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = TipoHabitacionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        try:
            context = self.get_context_data(form=form)
            formset = context['formset']
            if formset.is_valid():
                # Guardar el hotel primero
                self.object = form.save()
                # Guardar el formset
                formset.instance = self.object
                formset.save()
                messages.success(self.request, 'Hotel actualizado exitosamente')
                return HttpResponseRedirect(self.get_success_url())
            return self.render_to_response(context)
        except Exception as e:
            messages.error(self.request, f'Error al actualizar hotel: {str(e)}')
            return self.render_to_response(self.get_context_data(form=form))

class HotelListView(RoleAccessMixin, TemplateView):
    allowed_roles = ['admin', 'reservas']
    template_name = 'reservas/hotel_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hoteles'] = Hotel.objects.filter(activo=True).prefetch_related('tipohabitacion_set')
        return context

class HotelDetailView(RoleAccessMixin, DetailView):
    allowed_roles = ['admin', 'reservas']
    model = Hotel
    template_name = 'reservas/hotel_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['habitaciones'] = self.object.tipohabitacion_set.all()
        return context



class HotelDeleteView(RoleAccessMixin, DeleteView):
    allowed_roles = ['admin']
    model = Hotel
    template_name = 'reservas/hotel_confirm_delete.html'
    success_url = reverse_lazy('reservas:hotel_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Hotel eliminado exitosamente')
        return super().delete(request, *args, **kwargs)


class TipoHabitacionDeleteView(RoleAccessMixin, DeleteView):
    allowed_roles = ['admin', 'reservas']
    model = TipoHabitacion
    template_name = 'reservas/habitacion_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('reservas:hotel_detail', kwargs={'pk': self.object.hotel.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tipo de habitación eliminado exitosamente')
        return super().delete(request, *args, **kwargs)