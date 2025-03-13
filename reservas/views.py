from django.shortcuts import render
from django.views.generic import CreateView
from .models import Reserva
from .forms import ReservaForm, NinoFormSet, HabitacionForm
from .models import TipoHabitacion
from django.views.generic import CreateView
from django.http import JsonResponse
from .models import TipoHabitacion
from .forms import ReservaForm, NinoFormSet, HabitacionFormSet
from django.core.paginator import Paginator
from django.urls import reverse  # Para generar URLs
from .forms import ReservaForm, NinoFormSet, HabitacionFormSet


def reservas_home(request):
    reservas = Reserva.objects.select_related('cliente', 'empresa', 'hotel').order_by('-fecha_entrada')
    
    paginator = Paginator(reservas, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reservas/reservas_home.html', {
        'page_obj': page_obj,
        'request': request
    })


class CrearReservaView(CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/hotel_reserva.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['nino_formset'] = NinoFormSet(self.request.POST)
            context['habitacion_formset'] = HabitacionFormSet(self.request.POST)
        else:
            context['nino_formset'] = NinoFormSet()
            context['habitacion_formset'] = HabitacionFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        ninos = form.cleaned_data['ninos']
        nino_formset = context['nino_formset']
        habitacion_formset = context['habitacion_formset']
        
        if nino_formset.is_valid() and habitacion_formset.is_valid():
            self.object = form.save()
            
            # Validar cantidad de niños
            nino_count = sum(1 for form in nino_formset if not form.cleaned_data.get('DELETE', False))
            if nino_count != ninos:
                form.add_error('ninos', f'Debe ingresar {ninos} edades de niños')
                return self.form_invalid(form)
            
            nino_formset.instance = self.object
            nino_formset.save()
            
            # Validar habitaciones
            for habitacion in habitacion_formset:
                if habitacion.cleaned_data:
                    tipo = habitacion.cleaned_data['tipo_habitacion']
                    if tipo.hotel != self.object.hotel:
                        form.add_error(None, f"Habitación {tipo} no pertenece al hotel seleccionado")
                        return self.form_invalid(form)
            
            habitacion_formset.instance = self.object
            habitacion_formset.save()
            return super().form_valid(form)
        
        return self.form_invalid(form)
    def get_success_url(self):
        return reverse('reservas:reservas_home')

def get_habitaciones(request):
    hotel_id = request.GET.get('hotel_id')
    habitaciones = TipoHabitacion.objects.filter(hotel_id=hotel_id).values('id', 'nombre', 'precio_noche')
    return JsonResponse(list(habitaciones), safe=False)