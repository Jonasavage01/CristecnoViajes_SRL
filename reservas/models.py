from django.db import models
from crm.models import Cliente, Empresa
from usuarios.models import UsuarioPersonalizado

class Reserva(models.Model):
    TIPO_RESERVA_CHOICES = [
        ('hotel', 'Hotel/Resort'),
        ('tour', 'Tour'),
        ('transporte', 'Transporte'),
        ('otros', 'Otros')
    ]

    # Paso 1
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
    tipo_reserva = models.CharField(
        max_length=20, 
        choices=TIPO_RESERVA_CHOICES,
        default='hotel'
    )
    creado_por = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Paso 2
    fecha_entrada = models.DateField(null=True)
    fecha_salida = models.DateField(null=True)
    adultos = models.PositiveIntegerField(default=1)
    adolescentes = models.PositiveIntegerField(default=0)
    ninos = models.PositiveIntegerField(default=0)
    infantes = models.PositiveIntegerField(default=0)
    
    # Control
    paso_actual = models.PositiveIntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Reserva #{self.id} - {self.get_tipo_display()}"