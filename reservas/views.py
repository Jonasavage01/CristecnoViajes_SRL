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
            
            # Devolver JSON con URL de redirección
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
        cliente_id = request.POST.get('cliente_id')
        empresa_id = request.POST.get('empresa_id')
        
        if not cliente_id and not empresa_id:
            raise ValidationError('Debe seleccionar un cliente o empresa')
            
        return Reserva.objects.create(
            cliente_id=cliente_id,
            empresa_id=empresa_id,
            tipo_reserva=self.kwargs['tipo'],
            creado_por=request.user
        )

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

class Paso1SeleccionCliente(ReservaWizard):
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

class Paso2DatosHuespedes(TemplateView):
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

class BuscarClientesEmpresasView(View):
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
        
class LimpiarSeleccionView(View):
    def post(self, request, *args, **kwargs):
        if 'reserva_data' in request.session:
            del request.session['reserva_data']
        return JsonResponse({'success': True})

# views.py
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
    
class HotelHabitacionesView(View):
    def get(self, request, hotel_id):
        habitaciones = TipoHabitacion.objects.filter(hotel_id=hotel_id).values(
            'id', 'nombre', 'precio_noche', 'capacidad'
        )
        return JsonResponse(list(habitaciones), safe=False)

class HotelSearchView(View):
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