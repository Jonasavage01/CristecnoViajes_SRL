# models.py
from django.db import models
from django.core.exceptions import ValidationError
from crm.models import Cliente, Empresa

class Hotel(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    is_other = models.BooleanField(default=False, verbose_name="Es 'Otros'")

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']

class TipoHabitacion(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='tipos_habitacion')
    nombre = models.CharField(max_length=100)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    capacidad = models.PositiveIntegerField(default=2)
    
    def __str__(self):
        return f"{self.nombre} ({self.hotel})"

class Reserva(models.Model):
    TIPO_RESERVA_CHOICES = [
        ('cliente', 'Cliente'),
        ('empresa', 'Empresa'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_RESERVA_CHOICES)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    manual_hotel = models.CharField(max_length=100, blank=True)
    adultos = models.PositiveIntegerField(default=1)
    ninos = models.PositiveIntegerField(default=0)
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    tarifa_adulto = models.DecimalField(max_digits=10, decimal_places=2)
    tarifa_nino = models.DecimalField(max_digits=10, decimal_places=2)
    comision = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas_cliente = models.TextField(blank=True)
    notas_suplidor = models.TextField(blank=True)
    archivos = models.FileField(upload_to='reservas/archivos/', blank=True)
    
    def clean(self):
        # Validación de campos obligatorios
        if self.tipo == 'cliente' and not self.cliente:
            raise ValidationError("Se requiere un cliente para reservas individuales")
        if self.tipo == 'empresa' and not self.empresa:
            raise ValidationError("Se requiere una empresa para reservas corporativas")
        if self.hotel.is_other and not self.manual_hotel:
            raise ValidationError("Debe especificar el nombre del hotel")
        if self.fecha_salida <= self.fecha_entrada:
            raise ValidationError("La fecha de salida debe ser posterior a la entrada")
        
    @property
    def noches(self):
        return (self.fecha_salida - self.fecha_entrada).days
    
    @property
    def total(self):
        total_personas = (self.adultos * self.tarifa_adulto + self.ninos * self.tarifa_nino) * self.noches
        total_habitaciones = sum(
            hr.cantidad * hr.tipo_habitacion.precio_noche * self.noches 
            for hr in self.habitaciones_reserva.all()
        )
        return total_personas + total_habitaciones + (self.comision or 0)

class ReservaHabitacion(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='habitaciones_reserva')
    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

class Nino(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='ninos_reserva')
    edad = models.PositiveIntegerField()