from django.db import models
from django_countries.fields import CountryField
import datetime


class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('contactado', 'Contactado'),
        ('en_proceso', 'En Proceso'),
        ('convertido', 'Convertido'),
    ]

    nombre_apellido = models.CharField('Nombre y Apellido', max_length=200)
    cedula_pasaporte = models.CharField('Cédula/Pasaporte', max_length=20, unique=True)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento')
    nacionalidad = CountryField(
        'Nacionalidad',
        blank=False,  # Obligatorio
        default='VE'  # Opcional: valor por defecto (ej. Venezuela)
    )
    lugar_trabajo = models.CharField('Lugar de Trabajo', max_length=100, blank=True)
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    email = models.EmailField('Correo Electrónico', unique=True)
    direccion_fisica = models.TextField('Dirección Física')
    telefono = models.CharField('Teléfono', max_length=20)
    movil = models.CharField('Móvil', max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    ultima_actividad = models.DateTimeField(auto_now=True, verbose_name='Última Actividad')
    estado = models.CharField(
        'Estado del Lead',
        max_length=20,
        choices=ESTADO_CHOICES,
        default='nuevo'
    )
    notas = models.TextField(blank=True, verbose_name='Notas Adicionales')
    documento = models.FileField(
        'Documento Adjunto',
        upload_to='clientes/documentos/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['cedula_pasaporte']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.nombre_apellido

    def get_estado_color(self):
        color_map = {
            'nuevo': 'primary',
            'contactado': 'info',
            'en_proceso': 'warning',
            'convertido': 'success'
        }
        return color_map.get(self.estado, 'secondary')

    def get_edad(self):
        today = datetime.date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )