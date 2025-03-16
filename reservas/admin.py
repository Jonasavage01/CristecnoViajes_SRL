from django.contrib import admin
from .models import Hotel, TipoHabitacion, HabitacionReserva, Reserva

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'estrellas', 'activo')
    list_filter = ('activo', 'estrellas')
    search_fields = ('nombre', 'ubicacion')

@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'hotel', 'precio_noche', 'capacidad')
    list_filter = ('hotel',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_reserva', 'cliente', 'fecha_creacion')
    list_filter = ('tipo_reserva', 'paso_actual')
    search_fields = ('cliente__nombre', 'empresa__nombre')

@admin.register(HabitacionReserva)
class HabitacionReservaAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'tipo_habitacion', 'cantidad')
    list_filter = ('tipo_habitacion__hotel',)