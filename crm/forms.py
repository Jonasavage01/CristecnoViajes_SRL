import re
import datetime

from django import forms
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget

from .models import Cliente

class ClienteForm(forms.ModelForm):
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
        }
        help_texts = {
            'cedula_pasaporte': 'Formato: X-000-0000 (Ej: V-12345678)',
            'telefono': 'Incluir código de país (Ej: +58 412 1234567)',
            'email': 'Ejemplo: nombre@dominio.com',
            'documento': 'Formatos aceptados: PDF, DOC, DOCX (Máx. 5MB)',
        }
        labels = {
            'estado': 'Estado del Lead'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Verificar si el campo 'documento' existe antes de actualizar sus atributos
        if 'documento' in self.fields:
            self.fields['documento'].widget.attrs.update({'accept': '.pdf,.doc,.docx'})

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
            file_size = documento.size
            limit_mb = 5
            if file_size > limit_mb * 1024 * 1024:
                raise ValidationError(f"Tamaño máximo permitido: {limit_mb}MB")
        return documento

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not re.match(r'^\+?[\d\s()-]{7,15}$', telefono):
            raise ValidationError("Formato de teléfono inválido")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        self._validate_unique_email_and_cedula()
        return cleaned_data

    def _validate_unique_email_and_cedula(self):
        """Validación para asegurar unicidad en creación"""
        cedula = self.cleaned_data.get('cedula_pasaporte')
        email = self.cleaned_data.get('email')
        if cedula and Cliente.objects.filter(cedula_pasaporte=cedula).exists():
            self.add_error('cedula_pasaporte', 'Esta cédula/pasaporte ya está registrada')
        if email and Cliente.objects.filter(email=email).exists():
            self.add_error('email', 'Este correo electrónico ya está registrado')



class ClienteEditForm(ClienteForm):
    class Meta(ClienteForm.Meta):
        exclude = ['documento', 'notas', 'fecha_creacion', 'ultima_actividad']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos de solo lectura con estilo personalizado
        readonly_fields = ['cedula_pasaporte', 'email']
        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].widget.attrs.update({
                    'readonly': True,
                    'class': 'form-control-plaintext bg-dark text-white'
                })
                
        # Mejorar etiquetas y ayuda
        self.fields['telefono'].help_text = 'Formato: +CC (Código de país) Número'
        self.fields['movil'].help_text = 'Número completo con código de país'

    def clean(self):
        cleaned_data = super().clean()
        self._validate_unique_email_and_cedula()
        return cleaned_data

    def _validate_unique_email_and_cedula(self):
        """Validación de unicidad excluyendo la instancia actual"""
        cedula = self.cleaned_data.get('cedula_pasaporte')
        email = self.cleaned_data.get('email')
        
        if self.instance.pk:
            queryset = Cliente.objects.exclude(pk=self.instance.pk)
            
            if cedula and queryset.filter(cedula_pasaporte=cedula).exists():
                self.add_error('cedula_pasaporte', 'Esta cédula/pasaporte ya está registrada')
                
            if email and queryset.filter(email=email).exists():
                self.add_error('email', 'Este correo electrónico ya está registrado')