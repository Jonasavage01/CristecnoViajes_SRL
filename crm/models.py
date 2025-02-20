from django.db import models
from django_countries.fields import CountryField
import datetime
from django.contrib.auth.models import User



class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('potencial', 'Potencial'),  # Solo estos 3 estados
    ]

    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    cedula_pasaporte = models.CharField(
        'Cédula/Pasaporte', 
        max_length=20, 
        unique=True,
        help_text='Números para cédula dominicana o número de pasaporte internacional'
    )
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    nacionalidad = CountryField(
        'Nacionalidad',
        blank=False,  # Obligatorio
        default='DO'  # Opcional: valor por defecto (ej. Venezuela)
    )
    lugar_trabajo = models.CharField('Lugar de Trabajo', max_length=100, blank=True)
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    email = models.EmailField('Correo Electrónico', unique=True)
    direccion_fisica = models.TextField('Dirección Física')
    telefono = models.CharField(
        'Teléfono', 
        max_length=20,
        help_text='Formato internacional: +18091234567 o "N/A" si no aplica'
    )
    movil = models.CharField(
        'Móvil', 
        max_length=20,
        help_text='Formato internacional: +18091234567 o "N/A" si no aplica'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    ultima_actividad = models.DateTimeField(auto_now=True, verbose_name='Última Actividad')
    estado = models.CharField(
        'Estado del Lead',
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo' 
    )

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
        return f"{self.nombre} {self.apellido}"

    def get_estado_color(self):
        color_map = {
            'activo': 'success',
            'inactivo': 'secondary',
            'potencial': 'warning'
        }
        return color_map.get(self.estado, 'light')

    def get_edad(self):
        if not self.fecha_nacimiento:
            return "N/A"
        
        today = datetime.date.today()
        edad = today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
        return f"{edad} años"

class DocumentoCliente(models.Model):
    TIPO_CHOICES = [
        ('general', 'General'),
        ('contrato', 'Contrato'),
        ('identificacion', 'Identificación'),
        ('otros', 'Otros')
    ]
    
    cliente = models.ForeignKey(Cliente, related_name='documentos', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='clientes/documentos/%Y/%m/%d/')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Documento {self.get_tipo_display()} - {self.cliente}"

class NotaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, related_name='notas_cliente', on_delete=models.CASCADE)
    contenido = models.TextField('Contenido')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True  # Permite que el campo sea opcional
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Nota de Cliente'
        verbose_name_plural = 'Notas de Clientes'