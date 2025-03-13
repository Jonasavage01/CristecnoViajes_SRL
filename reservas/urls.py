from django.urls import path
from . import views
from .views import CrearReservaView, get_habitaciones

app_name = 'reservas'

urlpatterns = [
    path('', views.reservas_home, name='reservas_home'),
    path('nueva/', CrearReservaView.as_view(), name='crear_reserva'),
    path('get-habitaciones/', get_habitaciones, name='get_habitaciones'),
]