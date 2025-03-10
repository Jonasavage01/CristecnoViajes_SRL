# Standard library imports
import re
import datetime
import logging

# Django core imports
from django import forms
from django.core.exceptions import ValidationError
import re
import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Cliente
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
                    'class': 'form-control',
                    'placeholder': 'DD/MM/AAAA',
                    'pattern': '^\d{2}-\d{2}-\d{4}$'
                }
            ),
            'nacionalidad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(
                attrs={
                    'class': 'form-select',
                    'choices': Cliente.ESTADO_CHOICES
                }
            ),
            'notas': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ej: Preferencias de viaje, restricciones alimentarias...'
            }),
            'direccion_fisica': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Ej: Calle Principal #123, Ciudad, Estado'
            }),
            'telefono': forms.TextInput(attrs={
                'placeholder': '+18091234567 o N/A',
                'pattern': '^(\+[1-9]\d{1,14}|N/A)$'
            }),
            'movil': forms.TextInput(attrs={
                'placeholder': '+18091234567 o N/A',
                'pattern': '^(\+[1-9]\d{1,14}|N/A)$'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'nombre@dominio.com o N/A',
                'pattern': '^([^@\\s]+@[^@\\s]+\\.[^@\\s]+|N/A)$'
            }),
        }
        help_texts = {
            'cedula_pasaporte': mark_safe('📝 Formatos aceptados:<br>'
                                         '- Cédula: 402-1234567-8<br>'
                                         '- Pasaporte: PA1234567'),
            'documento': '📎 Formatos aceptados: PDF, DOC, DOCX (Máx. 5MB)',
        }
        labels = {
            'estado': '🏷 Estado del Lead',
            'nacionalidad': '🌍 Nacionalidad',
            'fecha_nacimiento': '🎂 Fecha de Nacimiento'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_form_control_class()
        self._set_custom_required_text()
        

    def _add_form_control_class(self):
        """Añade clase form-control a todos los campos"""
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def _set_custom_required_text(self):
        """Establece texto personalizado para campos obligatorios"""
        for field in self.fields.values():
            if field.required:
                field.widget.attrs['data-required-text'] = _('Este campo es requerido')

    def clean_cedula_pasaporte(self):
        data = self.cleaned_data['cedula_pasaporte'].upper().strip()
        
        if not data:
            raise ValidationError("🚨 Por favor ingrese la identificación")
            
        if len(data) < 6 or len(data) > 20:
            raise ValidationError("📏 La identificación debe tener entre 6 y 20 caracteres")
            
        if not re.match(r'^[A-Z0-9-]+$', data):
            raise ValidationError(
                mark_safe("🔠 Caracteres inválidos. Solo se permiten:<br>"
                         "- Letras mayúsculas (A-Z)<br>"
                         "- Números (0-9)<br>"
                         "- Guiones (-)")
            )
            
        return data

    def _clean_phone_field(self, field_name, value):
        value = value.strip().upper()
        
        if value == self.NA_CHOICE:
            return self.NA_CHOICE
            
        if not re.match(r'^(\+?[1-9]\d{1,14})$', value):
            raise ValidationError(
                mark_safe(f"📱 Formato inválido para {field_name}.<br>"
                          "Ejemplos válidos:<br>"
                          "- Internacional: +18091234567<br>"
                          "- Nacional: 8091234567")
            )
            
        return value

    def clean_telefono(self):
        return self._clean_phone_field('teléfono', self.cleaned_data.get('telefono', ''))

    def clean_movil(self):
        return self._clean_phone_field('móvil', self.cleaned_data.get('movil', ''))

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()  # Siempre a minúsculas
        if email == self.NA_CHOICE.lower():
        
            return self.NA_CHOICE
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise ValidationError(
                mark_safe("📧 Invalid email format.<br>Example: name@domain.com")
            )
        return email

    def _check_unique(self, field, value, error_message):
        """Verifica unicidad considerando mayúsculas/minúsculas para email"""
        if field == 'email':
            lookup = f"{field}__iexact" if field == 'email' else field  # Búsqueda insensible a mayúsculas
        else:
            lookup = field

        queryset = Cliente.objects.filter(**{lookup: value})
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            self.add_error(field, mark_safe(f"⛔ {error_message}"))

    def clean(self):
        cleaned_data = super().clean()
        self._normalize_na_values(cleaned_data)
        self._validate_contact_methods(cleaned_data)
        self._validate_unique_email_and_cedula()
    
    # Forzar validación de campos requeridos
        required_fields = ['nombre', 'apellido', 'cedula_pasaporte']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "Este campo es requerido")
    
        return cleaned_data

    def _normalize_na_values(self, cleaned_data):
        """Normaliza valores N/A a mayúsculas"""
        for field in ['telefono', 'movil', 'email']:
            value = cleaned_data.get(field, '')
            if isinstance(value, str) and value.strip().upper() == self.NA_CHOICE:
                cleaned_data[field] = self.NA_CHOICE

    def _validate_contact_methods(self, cleaned_data):
        """Valida al menos un método de contacto válido"""
        contact_fields = [
            cleaned_data.get('telefono', '') not in [self.NA_CHOICE, ''],
            cleaned_data.get('movil', '') not in [self.NA_CHOICE, ''],
            cleaned_data.get('email', '') not in [self.NA_CHOICE, '']
        ]
    
        if not any(contact_fields):
            raise ValidationError(
                mark_safe("📞❌ Debe proporcionar al menos un método de contacto válido:<br>"
                        "- Teléfono<br>"
                        "- Móvil<br>"
                        "- Email"),
                code='contacto_requerido'
            )

    def _validate_unique_email_and_cedula(self):
        """Valida la unicidad de email y cédula/pasaporte"""
        email = self.cleaned_data.get('email')
        cedula = self.cleaned_data.get('cedula_pasaporte')

        if email and email != self.NA_CHOICE:
            self._check_unique('email', email, 'Este correo ya está registrado')

        if cedula:
            self._check_unique('cedula_pasaporte', cedula, 'Esta identificación ya existe en el sistema')

    def _check_unique(self, field, value, error_message):
        """Verifica si un valor es único en la base de datos"""
        queryset = Cliente.objects.filter(**{field: value})
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            self.add_error(field, mark_safe(f"⛔ {error_message}"))

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        
        if fecha and fecha > datetime.date.today():
            raise ValidationError("📅 La fecha de nacimiento no puede ser futura")
            
        return fecha

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        
        if documento and documento.size > 5 * 1024 * 1024:
            raise ValidationError(
                mark_safe("📁 El archivo es demasiado grande.<br>"
                          "Tamaño máximo permitido: 5MB")
            )
            
        return documento

class ClienteEditForm(forms.ModelForm):
    NA_CHOICE = 'N/A'
    
    class Meta:
        model = Cliente
        exclude = ['documento', 'notas', 'fecha_creacion', 'ultima_actividad']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'nacionalidad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'direccion_fisica': forms.Textarea(attrs={'rows': 2}),
            'telefono': forms.TextInput(attrs={'pattern': '^(\+[1-9]\d{1,14}|N/A)$'}),
            'movil': forms.TextInput(attrs={'pattern': '^(\+[1-9]\d{1,14}|N/A)$'}),
            'email': forms.EmailInput(attrs={'pattern': '^([^@\\s]+@[^@\\s]+\\.[^@\\s]+|N/A)$'}),
        }
        help_texts = {
            'cedula_pasaporte': mark_safe('📝 Formatos aceptados:<br>'
                                         '- Cédula: 402-1234567-8<br>'
                                         '- Pasaporte: PA1234567'),
        }
        labels = {
            'estado': '🏷 Estado del Lead',
            'nacionalidad': '🌍 Nacionalidad',
            'fecha_nacimiento': '🎂 Fecha de Nacimiento'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuración común de campos
        phone_fields = ['telefono', 'movil']
        for field in phone_fields:
            self.fields[field].widget.attrs.update({
                'placeholder': 'Ej: +18091234567 o N/A',
                'class': 'form-control phone-input'
            })
            
        # Habilitar edición de campos únicos con validación visual
        unique_fields = ['cedula_pasaporte', 'email']
        for field in unique_fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control unique-field',
                'data-original-value': getattr(self.instance, field, '')
            })

    def clean(self):
        """Validación unificada con el formulario principal"""
        cleaned_data = super().clean()
        self._normalize_na_values(cleaned_data)
        self._validate_contact_methods(cleaned_data)
        return cleaned_data

    def _normalize_na_values(self, cleaned_data):
        """Normaliza valores N/A a mayúsculas"""
        for field in ['telefono', 'movil', 'email']:
            value = cleaned_data.get(field, '')
            if isinstance(value, str) and value.strip().upper() == self.NA_CHOICE:
                cleaned_data[field] = self.NA_CHOICE

    def _validate_contact_methods(self, cleaned_data):
        """Valida al menos un método de contacto válido"""
        contact_fields = [
            cleaned_data.get('telefono', '') not in [self.NA_CHOICE, ''],
            cleaned_data.get('movil', '') not in [self.NA_CHOICE, ''],
            cleaned_data.get('email', '') not in [self.NA_CHOICE, '']
        ]
    
        if not any(contact_fields):
            raise ValidationError(
                mark_safe("📞❌ Debe proporcionar al menos un método de contacto válido:<br>"
                        "- Teléfono<br>"
                        "- Móvil<br>"
                        "- Email"),
                code='contacto_requerido'
            )

    def _check_unique(self, field, value, error_message):
        """Método reutilizable para validar unicidad"""
        queryset = Cliente.objects.filter(**{field: value})
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            self.add_error(field, mark_safe(f"⛔ {error_message}"))

    def clean_cedula_pasaporte(self):
        data = self.cleaned_data['cedula_pasaporte'].upper().strip()
        
        if not data:
            raise ValidationError("🚨 Por favor ingrese la identificación")
            
        if len(data) < 6 or len(data) > 20:
            raise ValidationError("📏 La identificación debe tener entre 6 y 20 caracteres")
            
        if not re.match(r'^[A-Z0-9-]+$', data):
            raise ValidationError(
                mark_safe("🔠 Caracteres inválidos. Solo se permiten:<br>"
                         "- Letras mayúsculas (A-Z)<br>"
                         "- Números (0-9)<br>"
                         "- Guiones (-)")
            )
        
        self._check_unique('cedula_pasaporte', data, 'Esta identificación ya existe en el sistema')
        return data

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        
        # Manejo del valor placeholder
        if email == self.NA_CHOICE.lower():
            return self.NA_CHOICE

        # Validación de formato básico
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise ValidationError(
                mark_safe("📧 Formato de email inválido.<br>"
                          "Ejemplo válido: nombre@dominio.com")
            )

        # Validación de unicidad case-insensitive
        self._check_unique(
            field='email',
            value=email,
            error_message='Este correo ya está registrado'
        )
        
        return email

    def _check_unique(self, field, value, error_message):
        """Validación genérica de unicidad con búsqueda case-insensitive"""
        lookup = f'{field}__iexact'  # Busqueda insensible a mayúsculas
        
        # Excluimos la instancia actual si es edición
        queryset = Cliente.objects.filter(**{lookup: value})
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError(error_message)



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