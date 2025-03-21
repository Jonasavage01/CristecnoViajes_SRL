from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.reservas_home, name='reservas_home'),
    path('nueva/<str:tipo>/', views.ReservaWizard.as_view(), name='nueva_reserva'),
    path('nueva/<str:tipo>/paso-<int:paso>/', views.ReservaWizard.as_view(), name='wizard_paso'),
    path('api/buscar/', views.BuscarClientesEmpresasView.as_view(), name='buscar_clientes'),
    path('limpiar-seleccion/', views.LimpiarSeleccionView.as_view(), name='limpiar_seleccion'),
    path('api/hoteles/', views.HotelSearchView.as_view(), name='buscar_hoteles'),
     path('api/hoteles/<int:hotel_id>/habitaciones/', 
         views.HotelHabitacionesView.as_view(), 
         name='hotel_habitaciones'),
    path('agregar-hotel/', views.HotelCreateView.as_view(), name='agregar_hotel'),
    path('hoteles/', views.HotelListView.as_view(), name='hotel_list'),
    path('hoteles/<int:pk>/', views.HotelDetailView.as_view(), name='hotel_detail'),
     path('hoteles/<int:pk>/editar/', views.HotelUpdateView.as_view(), name='hotel_edit'),
    path('hoteles/<int:pk>/eliminar/', views.HotelDeleteView.as_view(), name='hotel_delete'),
    path('habitaciones/<int:pk>/eliminar/', views.TipoHabitacionDeleteView.as_view(), name='habitacion_delete'),
    

   
    
]