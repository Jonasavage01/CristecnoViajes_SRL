# reservas/models.py
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

    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Cliente asociado'
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Empresa asociada'
    )
    tipo_reserva = models.CharField(
        max_length=20, 
        choices=TIPO_RESERVA_CHOICES,
        default='hotel'
    )
    creado_por = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reservas_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        nombre = self.cliente.nombre if self.cliente else self.empresa.nombre_comercial
        return f"Reserva #{self.id} - {nombre}"