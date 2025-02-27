# empresas_forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
import re
import datetime
from .models import Empresa, DocumentoEmpresa
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
import os

class EmpresaForm(forms.ModelForm):
    NA_CHOICE = 'N/A'
    
    # Campo explícito para estado con choices correctamente definidos
    estado = forms.ChoiceField(
        choices=Empresa.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Estado de la Empresa'
    )
    
    class Meta:
        model = Empresa
        fields = '__all__'
        widgets = {
            'direccion_fisica': forms.Textarea(attrs={'rows': 2}),
            'telefono': forms.TextInput(attrs={
                'placeholder': 'Ej: 8091234567',
                'pattern': '^[1-9]\d{7,14}$'  # Patrón sin +
            }),
            'telefono2': forms.TextInput(attrs={
                'placeholder': 'Ej: 8091234567 (Opcional)',
                'pattern': '^(N/A|[1-9]\d{7,14})$'  # Patrón sin +
            }),
            'sitio_web': forms.URLInput(attrs={
                'placeholder': 'Ej: https://www.empresa.com'
            }),
            'documento': forms.FileInput(attrs={
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'rnc': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_electronica': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'rnc': 'Registro Nacional de Contribuyente',
            'telefono': 'Formato: 8-15 dígitos sin símbolos. Ej: 8091234567',
            'telefono2': 'Formato: 8-15 dígitos o N/A (Opcional)',
            'direccion_electronica': 'Ejemplo: empresa@dominio.com',
            'documento': 'Formatos aceptados: PDF, DOC, DOCX, JPG, JPEG, PNG (Máx. 5MB)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuración inicial de campos
        for field in ['rnc', 'direccion_electronica']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_rnc(self):
        data = self.cleaned_data['rnc'].strip()
    
        if not data:
         raise ValidationError("El RNC es obligatorio")
    
    # Permitir solo números y guiones
        if not re.match(r'^[\d-]+$', data):
            raise ValidationError("El RNC solo puede contener números y guiones")
    
    # Eliminar guiones para guardar en base de datos
        cleaned_data = data.replace('-', '')
        return cleaned_data

    def _clean_phone_field(self, field_name, value):
        value = value.strip().upper()
    
        if value == self.NA_CHOICE:
            return self.NA_CHOICE
        
    # Permitir números con o sin +
        if not re.match(r'^\+?\d{7,15}$', value):
            raise ValidationError(
                f"Formato inválido para {field_name}. Ejemplos válidos: 8091234567, +18091234567"
        )
        return value

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if not telefono:
            raise ValidationError("El teléfono principal es obligatorio")
        return self._clean_phone_field('teléfono principal', telefono)

    def clean_telefono2(self):
        telefono2 = self.cleaned_data.get('telefono2', '').strip()
        if not telefono2 or telefono2.upper() == self.NA_CHOICE:
            return self.NA_CHOICE
        return self._clean_phone_field('teléfono secundario', telefono2)

    def clean_direccion_electronica(self):
        email = self.cleaned_data.get('direccion_electronica', '').lower().strip()
        if not email:
            raise ValidationError("La dirección electrónica es obligatoria")
    
    # Validación más precisa
        if not re.match(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Formato de email inválido. Ejemplo válido: usuario@dominio.com")
        
        return email

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if documento:
        # Validar tipo de archivo
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            ext = os.path.splitext(documento.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    "Tipo de archivo no permitido. Formatos aceptados: " + 
                    ", ".join(ext.upper() for ext in valid_extensions)
             )
        
        # Validar tamaño
            max_size = 5 * 1024 * 1024  # 5MB
            if documento.size > max_size:
                raise ValidationError(
                f"Tamaño máximo permitido: {max_size/1024/1024}MB. " +
                f"Archivo actual: {documento.size/1024/1024:.2f}MB"
            )
        return documento

    def _validate_unique_rnc_and_email(self):
        """Validación de unicidad para RNC y Email"""
        rnc = self.cleaned_data.get('rnc')
        email = self.cleaned_data.get('direccion_electronica')
        
        if rnc:
            qs = Empresa.objects.filter(rnc__iexact=rnc)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('rnc', 'Este RNC ya está registrado')
        
        if email:
            qs = Empresa.objects.filter(direccion_electronica__iexact=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('direccion_electronica', 'Este email ya está registrado')

    def clean(self):
        cleaned_data = super().clean()
        
        # Manejar N/A en teléfono secundario
        if cleaned_data.get('telefono2', '').upper() == self.NA_CHOICE:
            cleaned_data['telefono2'] = self.NA_CHOICE
        
        # Validar unicidad
        self._validate_unique_rnc_and_email()
        
        return cleaned_data

class EmpresaEditForm(EmpresaForm):
    NA_CHOICE = 'N/A'
    class Meta(EmpresaForm.Meta):
        model = Empresa
        exclude = ['documento', 'fecha_registro', 'ultima_actividad']
        widgets = {
            'representante': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_representante': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos de solo lectura con estilo mejorado
        readonly_fields = ['rnc', 'direccion_electronica']
        for field in readonly_fields:
            if field in self.fields:
                current_value = getattr(self.instance, field, '')
                self.fields[field].widget.attrs.update({
                    'readonly': True,
                    'class': 'form-control-plaintext bg-light',
                    'data-original-value': current_value
                })

        # Configurar campos de teléfono
        phone_fields = ['telefono', 'telefono2']
        for field in phone_fields:
            self.fields[field].widget.attrs.update({
                'placeholder': 'Ej: +18091234567 o N/A',
                'class': 'form-control phone-input'
            })
            self.fields[field].help_text = 'Formato internacional o "N/A" si no aplica'
    
    def _validate_unique_rnc_and_email(self):
        """Validación mejorada para edición"""
        if not self.instance.pk:
            raise ValidationError("Operación inválida: Empresa no existe")
        
        rnc = self.cleaned_data.get('rnc')
        email = self.cleaned_data.get('direccion_electronica')

        # Validación de RNC
        if rnc:
            qs = Empresa.objects.filter(
                Q(rnc__iexact=rnc) & 
                ~Q(pk=self.instance.pk)  # Paréntesis corregido
            )
            if qs.exists():
                self.add_error('rnc', 'Este RNC ya está registrado')

        # Validación de email
        if email:
            qs = Empresa.objects.filter(
                Q(direccion_electronica__iexact=email) & 
                ~Q(pk=self.instance.pk)  # Paréntesis corregido
            )
            if qs.exists():
                self.add_error('direccion_electronica', 'Este email ya está registrado')

    def clean(self):
        cleaned_data = super().clean()
        
        # Ejecutar validación personalizada
        self._validate_unique_rnc_and_email()
        
        # Validación de contacto mínimo
        telefono = cleaned_data.get('telefono')
        telefono2 = cleaned_data.get('telefono2')
        email = cleaned_data.get('direccion_electronica')

        if (telefono == self.NA_CHOICE and
            telefono2 == self.NA_CHOICE and
            not email):
            raise ValidationError("Debe proporcionar al menos un método de contacto válido")
        
        return cleaned_data


class DocumentoEmpresaForm(forms.ModelForm):
    class Meta:
        model = DocumentoEmpresa
        fields = ['tipo', 'archivo']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Seleccione tipo de documento'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            })
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validación de tamaño
            if archivo.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('El archivo excede 5MB')
            
            # Validación de tipo de archivo
            ext = os.path.splitext(archivo.name)[1][1:].lower()
            if ext not in ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Formato de archivo no permitido')
                
        return archivo

    def save(self, commit=True, empresa=None, user=None):
        instance = super().save(commit=False)
        if empresa:
            instance.empresa = empresa
        if user:
            instance.subido_por = user
        if commit:
            instance.save()
        return instance  # Corregido: se removió el ':' adicional