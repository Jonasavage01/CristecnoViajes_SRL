from django import forms
from .models import Hotel, TipoHabitacion
from django.forms import inlineformset_factory

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['nombre', 'ubicacion',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
        
        }

class TipoHabitacionForm(forms.ModelForm):
    class Meta:
        model = TipoHabitacion
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Habitación Doble, Suite Presidencial'
            })
        }

TipoHabitacionFormSet = inlineformset_factory(
    Hotel,
    TipoHabitacion,
    form=TipoHabitacionForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)