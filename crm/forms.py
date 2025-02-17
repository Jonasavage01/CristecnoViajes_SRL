import re
import datetime
from django import forms
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget
from .models import Cliente

class ClienteForm(forms.ModelForm):
    NA_CHOICE = 'N/A'
    
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': datetime.date.today().strftime('%Y-%m-%d')
                }
            ),
            'nacionalidad': CountrySelectWidget(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
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
        if fecha and fecha > datetime.date.today():
            raise ValidationError("La fecha de nacimiento no puede ser futura.")
        if fecha and (datetime.date.today().year - fecha.year) < 18:
            raise ValidationError("El cliente debe ser mayor de edad.")
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
        # Actualizar placeholders y estilos
        phone_fields = ['telefono', 'movil']
        for field in phone_fields:
            self.fields[field].widget.attrs['placeholder'] = 'Ej: +18091234567 o N/A'
            self.fields[field].help_text = 'Formato internacional o "N/A" si no aplica'
        # Establecer campos de solo lectura
        readonly_fields = ['cedula_pasaporte', 'email']
        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].widget.attrs.update({
                    'readonly': True,
                    'class': 'form-control-plaintext bg-light'
                })

    def _validate_unique_email_and_cedula(self):
        cedula = self.cleaned_data.get('cedula_pasaporte')
        email = self.cleaned_data.get('email')
    
    # Solo para creación
        if not self.instance.pk:
            if cedula and Cliente.objects.filter(cedula_pasaporte__iexact=cedula).exists():
                self.add_error('cedula_pasaporte', 'Esta identificación ya está registrada')
        if email and Cliente.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'Este correo ya está registrado')
