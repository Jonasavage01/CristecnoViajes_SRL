# views.py
from django.shortcuts import render
# reservas/views.py
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.db.models import Q
from crm.models import Cliente, Empresa
from django.core.serializers import serialize



def reservas_home(request): 
    return render(request, 'reservas/reservas_home.html', {
       
    })

class LimpiarSeleccionView(View):
    def post(self, request, *args, **kwargs):
        if 'reserva_data' in request.session:
            del request.session['reserva_data']
        return JsonResponse({'success': True})


class SeleccionarClienteEmpresaView(TemplateView):
    template_name = 'reservas/seleccionar_cliente_empresa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reserva_data = self.request.session.get('reserva_data', {})
        
        if reserva_data.get('cliente_id'):
            cliente = Cliente.objects.get(id=reserva_data['cliente_id'])
            context['cliente_json'] = serialize('json', [cliente])
        
        if reserva_data.get('empresa_id'):
            empresa = Empresa.objects.get(id=reserva_data['empresa_id'])
            context['empresa_json'] = serialize('json', [empresa])
        
        return context
    
    def post(self, request, *args, **kwargs):
        cliente_id = request.POST.get('cliente_id')
        empresa_id = request.POST.get('empresa_id')
        
        if not cliente_id and not empresa_id:
            return JsonResponse({'error': 'Debe seleccionar un cliente o empresa'}, status=400)
        
        # Limpiar selección anterior
        if 'reserva_data' in request.session:
            del request.session['reserva_data']
        
        # Guardar nueva selección
        request.session['reserva_data'] = {
            'cliente_id': cliente_id,
            'empresa_id': empresa_id,
            'paso_actual': 1
        }
        
        return JsonResponse({'success': True, 'next_url': '/reservas/paso2/'})

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