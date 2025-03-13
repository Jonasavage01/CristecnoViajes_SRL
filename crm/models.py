# Standard library imports
import os
import uuid
import datetime
import shutil
from django.conf import settings
from django.core.exceptions import ValidationError
from django.conf import settings 

# Django database imports
from django.db import models

# Django authentication
from django.contrib.auth.models import User

# Django utilities
from django.utils.text import get_valid_filename

# Django validators
from django.core.validators import FileExtensionValidator

# Third-party package imports
from django_countries.fields import CountryField
import logging

logger = logging.getLogger(__name__)

from usuarios.models import UsuarioPersonalizado


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
    email = models.CharField(
    'Correo Electrónico', 
    max_length=254, 
    unique=True,
    help_text='Ejemplo: nombre@dominio.com o N/A'
)
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
    
    ultima_actividad = models.DateTimeField(auto_now=True, verbose_name='Última Actividad')
    estado = models.CharField(
        'Estado del Lead',
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo' 
    )
    creado_por = models.ForeignKey(
        UsuarioPersonalizado, 
        related_name='clientes_creados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Fecha de Creación'
    )
    ultima_edicion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Edición'
    )
    editado_por = models.ForeignKey(
        UsuarioPersonalizado,
        related_name='clientes_editados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Último Editor'
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
    def delete(self, *args, **kwargs):
        # Eliminar archivo principal del cliente
        if self.documento:
            documento_path = self.documento.path
            if os.path.isfile(documento_path):
                os.remove(documento_path)
        
        # Eliminar directorio de documentos
        document_dir = os.path.join(
            settings.MEDIA_ROOT, 
            'clientes/documentos', 
            f'cliente_{self.id}'
        )
        if os.path.exists(document_dir):
            shutil.rmtree(document_dir)
            
        super().delete(*args, **kwargs)


def documento_upload_to(instance, filename):
    """Función renombrada y definida fuera de la clase"""
    original_name = get_valid_filename(filename)
    name, ext = os.path.splitext(original_name)
    unique_name = f"{name}_{uuid.uuid4().hex[:6]}{ext}"
    return f"clientes/documentos/cliente_{instance.cliente.id}/{unique_name}"

class DocumentoCliente(models.Model):
    TIPO_CHOICES = [
        ('general', 'General'),
        ('contrato', 'Contrato'),
        ('identificacion', 'Identificación'),
        ('otros', 'Otros')
    ]
    
    cliente = models.ForeignKey(
        'Cliente', 
        related_name='documentos', 
        on_delete=models.CASCADE,
        verbose_name='Cliente'
    )
    
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='general',
        verbose_name='Tipo de documento'
    )
    
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de subida'
    )
    
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Subido por'
    )
    
    archivo = models.FileField(
        upload_to=documento_upload_to,  # Usar la función renombrada
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            )
        ],
        verbose_name='Archivo'
    )
    def __str__(self):
        return f"Documento {self.get_tipo_display()} - {self.cliente}"

    @property
    def extension(self):
        return os.path.splitext(self.archivo.name)[1][1:].upper()
    
    @property
    def nombre_archivo(self):
        return os.path.basename(self.archivo.name)
    
    @property
    def icon_class(self):
        icon_map = {
            'PDF': 'bi-file-earmark-pdf text-danger',
            'DOC': 'bi-file-earmark-word text-primary',
            'DOCX': 'bi-file-earmark-word text-primary',
            'JPG': 'bi-file-image text-success',
            'JPEG': 'bi-file-image text-success',
            'PNG': 'bi-file-image text-success',
        }
        return icon_map.get(self.extension, 'bi-file-earmark text-secondary')
    def delete(self, *args, **kwargs):
        # Eliminar archivo asociado
        if self.archivo:
            archivo_path = self.archivo.path
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
        super().delete(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Documento de cliente'
        verbose_name_plural = 'Documentos de clientes'
        ordering = ['-fecha_subida']  # Orden consistente
        indexes = [
            models.Index(fields=['cliente', 'tipo']),
        ]

class NotaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, related_name='notas_cliente', on_delete=models.CASCADE)
    contenido = models.TextField('Contenido')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True  # Permite que el campo sea opcional
    )

    class Meta:
        ordering = ['-fecha_creacion']
        get_latest_by = 'fecha_creacion'
        verbose_name = 'Nota de Cliente'
        verbose_name_plural = 'Notas de Clientes'
        

""" Empresas """

class Empresa(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('potencial', 'Potencial'),
    ]

    nombre_comercial = models.CharField('Nombre Comercial', max_length=200)
    razon_social = models.CharField('Razón Social', max_length=200)
    rnc = models.CharField(
        'RNC',
        max_length=20,
        unique=True,
        help_text='Registro Nacional de Contribuyente'
    )
    direccion_fisica = models.TextField('Dirección Física')
    direccion_electronica = models.EmailField('Dirección Electrónica', unique=True)
    telefono = models.CharField(
        'Teléfono Principal',
        max_length=20,
        help_text='Formato internacional: +18091234567'
    )
    telefono2 = models.CharField(
        'Teléfono Secundario',
        max_length=20,
        blank=True,
        help_text='Formato internacional: +18091234567 (Opcional)'
    )
    sitio_web = models.URLField('Sitio Web', blank=True)
    representante = models.CharField('Representante Legal', max_length=200)
    cargo_representante = models.CharField('Cargo del Representante', max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    ultima_actividad = models.DateTimeField(auto_now=True, verbose_name='Última Actividad')
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo'
    )

    documento = models.FileField(
        'Documento Adjunto',
        upload_to='empresas/documentos/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['nombre_comercial']),
            models.Index(fields=['rnc']),
            models.Index(fields=['direccion_electronica']),
            models.Index(fields=['estado', 'fecha_registro']),
        ]

    def clean(self):
        # Solo validar email
        if self.direccion_electronica.upper() == 'N/A':
            raise ValidationError({'direccion_electronica': 'El email no puede ser N/A'})

    def get_estado_color(self):
        color_map = {
            'activo': 'success',   # Verde
            'inactivo': 'secondary', # Gris
            'potencial': 'warning',   # Amarillo/naranja
        }
        return color_map.get(self.estado, 'light')

    def save(self, *args, **kwargs):
        """Normalización automática del RNC al guardar"""
        if self.rnc:
            self.rnc = self.rnc.replace('-', '').replace(' ', '')
        self.direccion_electronica = self.direccion_electronica.strip().lower()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            # Eliminar archivo principal de la empresa
            if self.documento:
                documento_path = self.documento.path
                if os.path.isfile(documento_path):
                    os.remove(documento_path)

            # Eliminar directorio de documentos
            document_dir = os.path.join(
                settings.MEDIA_ROOT,
                'empresas/documentos',
                f'empresa_{self.id}'
            )
            if os.path.exists(document_dir):
                shutil.rmtree(document_dir)

        except Exception as e:
            logger.error(f"Error eliminando archivos de empresa: {str(e)}")

        finally:
            # Eliminar el objeto de la base de datos
            super().delete(*args, **kwargs)


def documento_empresa_upload_to(instance, filename):
    original_name = get_valid_filename(filename)
    name, ext = os.path.splitext(original_name)
    unique_name = f"{name}_{uuid.uuid4().hex[:6]}{ext}"
    return f"empresas/documentos/empresa_{instance.empresa.id}/{unique_name}"


class DocumentoEmpresa(models.Model):
    TIPO_CHOICES = [
        ('general', 'General'),
        ('contrato', 'Contrato'),
        ('rnc', 'RNC'),
        ('otros', 'Otros')
    ]
    
    empresa = models.ForeignKey(
        'Empresa', 
        related_name='documentos_empresa', 
        on_delete=models.CASCADE,
        verbose_name='Empresa'
    )
    
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='general',
        verbose_name='Tipo de documento'
    )
    
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de subida'
    )
    
    subido_por = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.SET_NULL, 
    null=True,
    blank=True,
    verbose_name='Subido por'
)
    
    archivo = models.FileField(
        upload_to=documento_empresa_upload_to,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            )
        ],
        verbose_name='Archivo'
    )

    # Mantenemos todas las propiedades igual que en DocumentoCliente
    def __str__(self):
        return f"Documento {self.get_tipo_display()} - {self.empresa}"

    @property
    def extension(self):
        return os.path.splitext(self.archivo.name)[1][1:].lower()
    
    @property
    def nombre_archivo(self):
        return os.path.basename(self.archivo.name)
    
    @property

    def icon_class(self):
        icon_map = {
            'pdf': 'bi-file-earmark-pdf text-danger',
            'doc': 'bi-file-earmark-word text-primary',
            'docx': 'bi-file-earmark-word text-primary',
            'jpg': 'bi-file-image text-success',
            'jpeg': 'bi-file-image text-success',
            'png': 'bi-file-image text-success'
        }
        return icon_map.get(self.extension.lower(), 'bi-file-earmark text-secondary')

    class Meta:
        verbose_name = 'Documento de empresa'
        verbose_name_plural = 'Documentos de empresas'
        ordering = ['-fecha_subida']
        indexes = [
            models.Index(fields=['empresa', 'tipo']),
        ]

class NotaEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, related_name='notas_empresa', on_delete=models.CASCADE)
    contenido = models.TextField('Contenido')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # En NotaEmpresa
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-fecha_creacion']
        get_latest_by = 'fecha_creacion'
        verbose_name = 'Nota de Empresa'
        verbose_name_plural = 'Notas de Empresas'
        

    def __str__(self):
        return f"Nota {self.fecha_creacion} - {self.empresa}"