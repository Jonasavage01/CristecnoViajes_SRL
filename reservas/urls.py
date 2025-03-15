from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.reservas_home, name='reservas_home'),
    path('nueva/<str:tipo>/', views.ReservaWizard.as_view(), name='nueva_reserva'),
    path('nueva/<str:tipo>/paso-<int:paso>/', views.ReservaWizard.as_view(), name='wizard_paso'),
    path('api/buscar/', views.BuscarClientesEmpresasView.as_view(), name='buscar_clientes'),
    path('limpiar-seleccion/', views.LimpiarSeleccionView.as_view(), name='limpiar_seleccion'),
]