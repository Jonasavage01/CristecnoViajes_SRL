# Standard library imports
import re
import datetime
import logging

# Django core imports
from django import forms
from django.core.exceptions import ValidationError

# Django database imports
from django.db.models import Q

# Third-party package imports
from django_countries.widgets import CountrySelectWidget

# Project-specific imports: Models
from .models import Cliente, DocumentoCliente

logger = logging.getLogger(__name__)


class ClienteForm(forms.ModelForm):
    NA_CHOICE = 'N/A'
    
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
             'fecha_nacimiento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': datetime.date.today().strftime('%Y-%m-%d'),
                    'required': False  # Hacerlo opcional
                }
            ),
            'nacionalidad': CountrySelectWidget(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={
                'class': 'form-select',
                'choices': Cliente.ESTADO_CHOICES  # Asegurar que use las opciones del modelo
            }),
            'notas': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ingrese observaciones relevantes...'}),
            'direccion_fisica': forms.Textarea(attrs={'rows': 2}),
            'telefono': forms.TextInput(attrs={
                'placeholder': 'Ej: +18091234567 o N/A',
                'pattern': '^(\+[1-9]\d{1,14}|N/A)$'
            }),
            'movil': forms.TextInput(attrs={
                'placeholder': 'Ej: +18091234567 o N/A',
                'pattern': '^(\+[1-9]\d{1,14}|N/A)$'
            }),
        }
        help_texts = {
            'cedula_pasaporte': 'Permite números y letras para pasaportes internacionales',
            'telefono': 'Números con + opcional para internacional. Ej: 18091234567 ó +18091234567',
            'movil': 'Números con + opcional para internacional. Ej: 18091234567 ó +18091234567',
            'email': 'Ejemplo: nombre@dominio.com',
            'documento': 'Formatos aceptados: PDF, DOC, DOCX (Máx. 5MB)',
        }
        labels = {
            'estado': 'Estado del Lead'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Elimina la configuración de readonly
        if 'email' in self.fields:
            self.fields['email'].widget.attrs.pop('readonly', None)
            self.fields['email'].widget.attrs.update({'class': 'form-control'})
        
        if 'cedula_pasaporte' in self.fields:
            self.fields['cedula_pasaporte'].widget.attrs.pop('readonly', None)
            self.fields['cedula_pasaporte'].widget.attrs.update({'class': 'form-control'})

    def clean_cedula_pasaporte(self):
        data = self.cleaned_data['cedula_pasaporte'].upper().strip()
        # Validación de requerido
        if not data:
            raise ValidationError("Este campo es obligatorio")
        # Validación de formato (mejorada)
        if not re.match(r'^[A-Z0-9-]{6,20}$', data):
            raise ValidationError("Formato inválido. Ejemplos válidos: 402-1234567-8, PA1234567")
        # Validación de caracteres permitidos
        if not re.match(r'^[A-Z0-9-]+$', data):
            raise ValidationError("Solo se permiten letras, números y guiones")
        return data

    def _clean_phone_field(self, field_name, value):
        value = value.strip().upper()
        if value == self.NA_CHOICE:
            return self.NA_CHOICE
    # Nueva regex que permite + opcional pero no lo requiere
        pattern = r'^(\+?[1-9]\d{1,14}|N/A)$'  # <- Cambio clave aquí
        if not re.match(pattern, value):
            raise ValidationError(
                f"Formato inválido para {field_name}. Ejemplos válidos: +18091234567 ó 18091234567"
        )
        return value

    def clean_telefono(self):
        return self._clean_phone_field('teléfono', self.cleaned_data.get('telefono', ''))

    def clean_movil(self):
        return self._clean_phone_field('móvil', self.cleaned_data.get('movil', ''))

    def _validate_unique_email_and_cedula(self):
        """Validación de unicidad considerando la instancia actual"""
        cedula = self.cleaned_data.get('cedula_pasaporte')
        email = self.cleaned_data.get('email')
        
        if cedula:
            qs = Cliente.objects.filter(cedula_pasaporte__iexact=cedula).exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('cedula_pasaporte', 'Esta identificación ya está registrada')
        
        if email:
            qs = Cliente.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('email', 'Este correo ya está registrado')
                
    def clean(self):
        cleaned_data = super().clean()
        # Actualizar campos si contienen "N/A"
        for field in ['telefono', 'movil', 'email']:
            if cleaned_data.get(field, '').strip().upper() == self.NA_CHOICE:
                cleaned_data[field] = self.NA_CHOICE
        # Validar que al menos un método de contacto esté presente
        if (cleaned_data.get('telefono') == self.NA_CHOICE and
            cleaned_data.get('movil') == self.NA_CHOICE and
            not cleaned_data.get('email')):
            raise ValidationError("Debe proporcionar al menos un método de contacto válido")
        # Validación de unicidad de cédula y email
        self._validate_unique_email_and_cedula()
        return cleaned_data

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        # Permitir N/A
        if fecha is None or fecha == self.NA_CHOICE:
            return None
        if fecha > datetime.date.today():
            raise ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if documento:
            if documento.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("Tamaño máximo permitido: 5MB")
        return documento

class ClienteEditForm(ClienteForm):
    class Meta(ClienteForm.Meta):
        exclude = ['documento', 'notas', 'fecha_creacion', 'ultima_actividad']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(f"Inicializando formulario de edición - Instancia PK: {self.instance.pk if self.instance else 'Nueva'}")
        
        # Configurar campos de teléfono
        phone_fields = ['telefono', 'movil']
        for field in phone_fields:
            self.fields[field].widget.attrs.update({
                'placeholder': 'Ej: +18091234567 o N/A',
                'class': 'form-control phone-input'
            })
            self.fields[field].help_text = 'Formato internacional o "N/A" si no aplica'

        # Campos de solo lectura con valores iniciales
        readonly_fields = ['cedula_pasaporte', 'email']
        for field in readonly_fields:
            if field in self.fields:
                current_value = getattr(self.instance, field, '')
                self.fields[field].widget.attrs.update({
                    'readonly': True,
                    'class': 'form-control-plaintext bg-light',
                    'data-original-value': current_value
                })
                logger.debug(f"Campo {field} configurado como readonly - Valor: {current_value}")

    def _validate_unique_email_and_cedula(self):
        """Validación mejorada con depuración y manejo de N/A"""
        logger.debug("Iniciando validación de unicidad...")
        
        if not self.instance.pk:
            logger.error("Validación fallida: No hay instancia asociada")
            raise ValidationError("Operación inválida: Cliente no existe")

        cedula = self.cleaned_data.get('cedula_pasaporte')
        email = self.cleaned_data.get('email')

        logger.debug(f"Datos a validar - Cédula: {cedula} | Email: {email}")
        logger.debug(f"Instancia actual - PK: {self.instance.pk}")

        # Validación de cédula
        if cedula:
            qs = Cliente.objects.filter(
                Q(cedula_pasaporte__iexact=cedula) & 
                ~Q(pk=self.instance.pk)
            )  # Corregido: paréntesis de cierre
            if qs.exists():
                logger.warning(f"Cédula duplicada detectada: {cedula}")
                self.add_error('cedula_pasaporte', 'Esta identificación ya está registrada')

        # Validación de email (excepto para N/A)
        if email and email.upper() != 'N/A':
            qs = Cliente.objects.filter(
                Q(email__iexact=email) & 
                ~Q(pk=self.instance.pk)
            )  # Corregido: paréntesis de cierre
            if qs.exists():
                logger.warning(f"Email duplicado detectado: {email}")
                self.add_error('email', 'Este correo ya está registrado')

        logger.debug("Validación de unicidad completada")

    def clean(self):
        """Método clean principal con depuración"""
        logger.debug("Ejecutando clean() del formulario de edición")
        cleaned_data = super().clean()
        
        try:
            self._validate_unique_email_and_cedula()
        except ValidationError as e:
            logger.error(f"Error en validación única: {str(e)}")
            raise

        # Depuración de datos limpios
        logger.debug("Datos limpios del formulario:")
        for key, value in cleaned_data.items():
            logger.debug(f"{key}: {value}")

        return cleaned_data



class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoCliente
        fields = ['tipo', 'archivo']
        
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validación de tamaño
            if archivo.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('El archivo excede 5MB')
        return archivo