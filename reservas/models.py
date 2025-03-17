from django.db import models
from crm.models import Cliente, Empresa
from usuarios.models import UsuarioPersonalizado
from django.core.exceptions import ValidationError

from django.db import models
from django.core.exceptions import ValidationError
from crm.models import Cliente, Empresa
from usuarios.models import UsuarioPersonalizado

class Hotel(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.ubicacion})"

class TipoHabitacion(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)  # Eliminar unique=True
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if TipoHabitacion.objects.filter(
            hotel=self.hotel, 
            nombre__iexact=self.nombre
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                'Ya existe un tipo de habitación con este nombre en el mismo hotel'
            )
    
    class Meta:
        unique_together = ('hotel', 'nombre')  # Añadir esta restricción
    
    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    TIPO_RESERVA_CHOICES = [
        ('hotel', 'Hotel/Resort'),
        ('tour', 'Tour'),
        ('transporte', 'Transporte'),
        ('otros', 'Otros')
    ]

    # Relaciones
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    creado_por = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Campos
    tipo_reserva = models.CharField(
        max_length=20, 
        choices=TIPO_RESERVA_CHOICES,
        default='hotel'
    )
    fecha_entrada = models.DateField(null=True)
    fecha_salida = models.DateField(null=True)
    adultos = models.PositiveIntegerField(default=1)
    adolescentes = models.PositiveIntegerField(default=0)
    ninos = models.PositiveIntegerField(default=0)
    infantes = models.PositiveIntegerField(default=0)
    paso_actual = models.PositiveIntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        
    def clean(self):
        if self.fecha_salida and self.fecha_entrada:
            if self.fecha_salida <= self.fecha_entrada:
                raise ValidationError({'fecha_salida': 'Debe ser posterior a fecha de entrada'})
        if self.adultos < 1:
            raise ValidationError({'adultos': 'Se requiere al menos 1 adulto'})

    def __str__(self):
        return f"Reserva #{self.id} - {self.get_tipo_display()}"

class HabitacionReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='habitaciones')
    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name_plural = "Habitaciones reservadas"
        constraints = [
            models.UniqueConstraint(
                fields=['reserva', 'tipo_habitacion'],
                name='unique_habitacion_por_reserva'
            )
        ]
    
    def clean(self):
        if self.cantidad < 1:
            raise ValidationError("La cantidad debe ser al menos 1")
            
    def __str__(self):
        return f"{self.cantidad}x {self.tipo_habitacion.nombre}"