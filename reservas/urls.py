from django.urls import path
from . import views


app_name = 'reservas'

urlpatterns = [
    path('nueva/<str:tipo>/', views.ReservaWizardView.as_view(), name='nueva_reserva'),
    path('api/buscar-clientes/', views.BuscarClientesEmpresasView.as_view(), name='buscar_clientes'),
    path('api/limpiar-seleccion/', views.LimpiarSeleccionView.as_view(), name='limpiar_seleccion'),
]