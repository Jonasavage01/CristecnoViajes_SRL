from django import forms
from django.core.exceptions import ValidationError
import datetime
from .models import Cliente
from django_countries.widgets import CountrySelectWidget

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
    if not re.match(r'^\+?[\d\s()-]{7,15}$', telefono):
        raise ValidationError("Formato de teléfono inválido")
    return telefono