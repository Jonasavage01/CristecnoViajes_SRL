# forms.py
from django import forms
from django_select2.forms import ModelSelect2Widget
from .models import Reserva, Hotel, TipoHabitacion, Nino, ReservaHabitacion
from crm.models import Cliente, Empresa

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'tipo', 'cliente', 'empresa', 'hotel', 'manual_hotel',
            'adultos', 'ninos', 'fecha_entrada', 'fecha_salida',
            'tarifa_adulto', 'tarifa_nino', 'comision',
            'notas_cliente', 'notas_suplidor', 'archivos'
        ]
        widgets = {
            'fecha_entrada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}),
             
            'cliente': ModelSelect2Widget(
                search_fields=['nombre__icontains', 'cedula_pasaporte__icontains'],
                attrs={'class': 'select2'}
            ),
            'empresa': ModelSelect2Widget(
                search_fields=['nombre_comercial__icontains', 'rnc__icontains'],
                attrs={'class': 'select2'}
            ),
            'hotel': ModelSelect2Widget(
                search_fields=['nombre__icontains'],
                attrs={'class': 'select2', 'data-minimum-input-length': 0}
            ),
        
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['empresa'].required = False
        self.fields['cliente'].required = False
        self.fields['hotel'].queryset = Hotel.objects.all()
        
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        hotel = cleaned_data.get('hotel')
        
        if tipo == 'cliente' and not cleaned_data.get('cliente'):
            self.add_error('cliente', 'Seleccione un cliente')
        if tipo == 'empresa' and not cleaned_data.get('empresa'):
            self.add_error('empresa', 'Seleccione una empresa')
        if hotel and hotel.is_other and not cleaned_data.get('manual_hotel'):
            self.add_error('manual_hotel', 'Especifique el nombre del hotel')

class NinoForm(forms.ModelForm):
    class Meta:
        model = Nino
        fields = ['edad']
        widgets = {'edad': forms.NumberInput(attrs={'min': 1, 'max': 17})}

NinoFormSet = forms.inlineformset_factory(
    Reserva, Nino, form=NinoForm, 
    extra=0, min_num=1, validate_min=True, 
    can_delete=True
)

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = ReservaHabitacion
        fields = ['tipo_habitacion', 'cantidad']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_habitacion'].queryset = TipoHabitacion.objects.none()

HabitacionFormSet = forms.inlineformset_factory(
    Reserva, ReservaHabitacion, form=HabitacionForm,
    extra=1, min_num=1, validate_min=True
)