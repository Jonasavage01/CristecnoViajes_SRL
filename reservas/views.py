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
            return redirect('reservas:wizard_paso', tipo=reserva.tipo_reserva, paso=next_paso)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

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
        reserva = Reserva.objects.get(id=request.session['reserva_id'])
        reserva.fecha_entrada = request.POST['fecha_entrada']
        reserva.fecha_salida = request.POST['fecha_salida']
        reserva.adultos = int(request.POST.get('adultos', 1))
        reserva.adolescentes = int(request.POST.get('adolescentes', 0))
        reserva.ninos = int(request.POST.get('ninos', 0))
        reserva.infantes = int(request.POST.get('infantes', 0))
        reserva.paso_actual = 2
        reserva.save()
        return reserva

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

class Paso2DatosHuespedes(ReservaWizard):
    step = 2
    
    def post(self, request, *args, **kwargs):
        try:
            self.reserva.fecha_entrada = request.POST['fecha_entrada']
            self.reserva.fecha_salida = request.POST['fecha_salida']
            self.reserva.adultos = int(request.POST.get('adultos', 1))
            self.reserva.adolescentes = int(request.POST.get('adolescentes', 0))
            self.reserva.ninos = int(request.POST.get('ninos', 0))
            self.reserva.infantes = int(request.POST.get('infantes', 0))
            self.reserva.paso_actual = 3
            self.reserva.save()
            return redirect('reservas:wizard_paso', tipo=self.kwargs['tipo'], paso=3)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
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