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
import logging
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Empresa, NotaEmpresa
import uuid

logger = logging.getLogger(__name__)

class EmpresaForm(forms.ModelForm):
    NA_CHOICE = 'N/A'
    DOC_MAX_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    
    estado = forms.ChoiceField(
        choices=Empresa.ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-style': 'btn-primary'
        }),
        label='Estado de la Empresa'
    )
    
    class Meta:
        model = Empresa
        fields = '__all__'
        widgets = {
            'nombre_comercial': forms.TextInput(attrs={'autofocus': True}),
            'direccion_fisica': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Ej: Calle Principal #123, Ciudad, Provincia'
            }),
            'telefono': forms.TextInput(attrs={
                'placeholder': '+18091234567 o 8091234567',
                'pattern': '^(\+|00)?[1-9]\d{7,14}$'
            }),
            'telefono2': forms.TextInput(attrs={
                'placeholder': '+18091234567 o 8091234567 (Opcional)',
                'pattern': '^(\+|00)?[1-9]\d{7,14}$|^N/A$'
            }),
            'sitio_web': forms.URLInput(attrs={
                'placeholder': 'https://www.ejemplo.com'
            }),
            
            'rnc': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '^[\d-]+$'
            }),
            'direccion_electronica': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@dominio.com'
            }),
        }
        help_texts = {
            'rnc': _('Registro Nacional de Contribuyente (solo números y guiones)'),
            'telefono': _('Formato internacional: +18091234567 o nacional: 8091234567'),
            
            },
        
        error_messages = {
            'direccion_electronica': {
                'unique': _("Esta dirección de correo electrónico ya está registrada.")
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_required_fields()
        self._add_form_control_class()

    def _set_required_fields(self):
        for field in ['nombre_comercial', 'razon_social', 'rnc', 'direccion_electronica', 'telefono']:
            self.fields[field].required = True
            self.fields[field].widget.attrs['required'] = 'required'

    def _add_form_control_class(self):
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')

    def clean_rnc(self):
        rnc = self.cleaned_data['rnc'].strip().replace('-', '')
        
        if not rnc.isdigit():
            raise ValidationError(_("El RNC solo puede contener números y guiones"))
            
        if len(rnc) < 9 or len(rnc) > 11:
            raise ValidationError(_("El RNC debe tener entre 9 y 11 dígitos"))
            
        if Empresa.objects.filter(rnc=rnc).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError(_("Este RNC ya está registrado"))
            
        return rnc

    def _clean_phone(self, value, field_name):
        value = value.strip()
        if value.upper() == self.NA_CHOICE:
            return self.NA_CHOICE
            
        if not value:
            if field_name == 'telefono':
                raise ValidationError(_("El teléfono principal es obligatorio"))
            return ''
            
        # Validar formato internacional o nacional
        if not re.match(r'^(\+?[1-9]\d{7,14}|00[1-9]\d{7,14})$', value):
            raise ValidationError(_(
                "Formato inválido. Ejemplos válidos: %(examples)s"
            ) % {'examples': '+18091234567, 8091234567'})
            
        return value

    def clean_telefono(self):
        return self._clean_phone(self.cleaned_data['telefono'], 'telefono')

    def clean_telefono2(self):
        return self._clean_phone(self.cleaned_data.get('telefono2', ''), 'telefono2')

    def clean_direccion_electronica(self):
        email = self.cleaned_data.get('direccion_electronica', '').lower().strip()
        if not email:
            raise ValidationError("La dirección electrónica es obligatoria")
    
    # Validación más precisa
        if not re.match(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Formato de email inválido. Ejemplo válido: usuario@dominio.com")
        
        return email

    def clean(self):
        cleaned_data = super().clean()
        self._normalize_na_values(cleaned_data)
        return cleaned_data

    def _normalize_na_values(self, cleaned_data):
        for field in ['telefono2']:
            value = cleaned_data.get(field, '')
            if isinstance(value, str) and value.upper() == self.NA_CHOICE:
                cleaned_data[field] = self.NA_CHOICE


class EmpresaEditForm(forms.ModelForm):
    NA_CHOICE = 'N/A'
    
    class Meta:
        model = Empresa
        fields = '__all__'
        exclude = ['documento', 'fecha_registro', 'ultima_actividad']
        widgets = {
            
            'rnc': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_electronica': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Extraer el user antes de inicializar el formulario
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self._setup_phone_fields()
        self._remove_readonly_attrs()
        self._add_help_texts()
        
        if self.user:
            logger.debug(f"Instancia en formulario - PK: {self.instance.pk if self.instance else 'None'}")
        logger.debug(f"Datos iniciales RNC: {self.initial.get('rnc')}")
        logger.debug(f"Valor inicial email: {self.initial.get('direccion_electronica')}")

    def _setup_phone_fields(self):
        """Configuración de campos telefónicos con validación mejorada"""
        phone_fields = ['telefono', 'telefono2']
        pattern = r'^(\+?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}|N/A)$'
        
        for field in phone_fields:
            self.fields[field].widget.attrs.update({
                'placeholder': 'Ej: +1 (809) 123-4567 o N/A',
                'class': 'form-control phone-input',
                'pattern': r'^(N/A|[1-9]\d{7,14})$', # Agrega 'r' aquí
                'title': 'Formato internacional: +[código país][número]'
            })
            self.fields[field].help_text = 'Ejemplos válidos: +18091234567, 8091234567, N/A'

    def _remove_readonly_attrs(self):
        """Elimina atributos de solo lectura y ajusta clases CSS"""
        for field_name, field in self.fields.items():
            attrs = field.widget.attrs
            if 'readonly' in attrs:
                del attrs['readonly']
            if 'form-control-plaintext' in attrs.get('class', ''):
                attrs['class'] = attrs['class'].replace('form-control-plaintext', 'form-control')
                attrs['style'] = 'cursor: text; background-color: #f8f9fa !important;'

    def _validate_unique_rnc_and_email(self):
        """Validación mejorada con normalización consistente"""
        rnc = self.cleaned_data.get('rnc', '')
        email = self.cleaned_data.get('direccion_electronica', '').strip().lower()

        # Obtener valores originales normalizados
        original_rnc = self.instance.rnc if self.instance else ''
        original_email = self.instance.direccion_electronica.lower() if self.instance.direccion_electronica else ''

        # Solo validar si hay cambios reales
        if rnc != original_rnc:
            if Empresa.objects.filter(rnc=rnc).exclude(pk=self.instance.pk).exists():
                self.add_error('rnc', 'Este RNC ya está registrado')

        if email != original_email:
            if Empresa.objects.filter(direccion_electronica__iexact=email).exclude(pk=self.instance.pk).exists():
                self.add_error('direccion_electronica', 'Este email ya está registrado')

    def _validate_rnc_format(self):
        """Validación flexible de formato"""
        rnc = self.cleaned_data.get('rnc', '')
        if rnc:
            if not re.match(r'^[\d-]+$', rnc):
                self.add_error('rnc', 'Solo se permiten números y guiones')
                
    def _normalize_rnc(self):
        """Normalización consistente con el modelo"""
        rnc = self.cleaned_data.get('rnc', '')
        if rnc:
            self.cleaned_data['rnc'] = rnc.replace('-', '').replace(' ', '')
            
    def _add_help_texts(self):
        """Actualiza textos de ayuda con información más clara"""
        help_texts = {
            'rnc': 'RNC de 9 dígitos sin guiones',
            'direccion_electronica': 'Correo electrónico válido (no se permite N/A)',
            'estado': 'Estado actual en el sistema',
            'telefono': 'Teléfono principal de contacto',
            'telefono2': 'Teléfono secundario (opcional)'
        }
        
        for field, text in help_texts.items():
            if field in self.fields:
                self.fields[field].help_text = text

    def clean(self):
        """Ejecuta todas las validaciones personalizadas"""
        cleaned_data = super().clean()
        
        # Ejecutar validaciones en orden específico
        validation_sequence = [
            self._normalize_na_values,
            self._validate_rnc_format,
            self._validate_contact_methods,
            self._validate_unique_rnc_and_email
        ]
        
        for validation in validation_sequence:
            if not self.errors:  # Solo continuar si no hay errores
                validation()
            else:
                break

        return cleaned_data


    def _validate_contact_methods(self):
        """Valida métodos de contacto con lógica mejorada"""
        contact_data = {
            'teléfono': self.cleaned_data.get('telefono', '').strip(),
            'teléfono secundario': self.cleaned_data.get('telefono2', '').strip(),
            'email': self.cleaned_data.get('direccion_electronica', '').strip().lower()
        }

        valid_contacts = [
            value for key, value in contact_data.items() 
            if value and value != self.NA_CHOICE
        ]

        if not valid_contacts:
            error_msg = (
                "Se requiere al menos un método de contacto válido: "
                "teléfono principal, secundario o email"
            )
            self.add_error(None, error_msg)
            logger.error("Falta método de contacto válido")

    def _validate_rnc_format(self):
        """Validación de formato RNC: números y guiones"""
        rnc = self.cleaned_data.get('rnc', '')
        if rnc:
            # Permitir números y guiones, sin longitud fija
            if not re.match(r'^[\d-]+$', rnc):
                self.add_error(
                    'rnc', 
                    'Solo se permiten números y guiones (-)'
                )
                logger.warning(f"Formato RNC inválido: {rnc}")

    def _normalize_rnc(self):
        """Normalizar RNC: quitar guiones y espacios"""
        rnc = self.cleaned_data.get('rnc', '')
        if rnc:
            self.cleaned_data['rnc'] = rnc.replace('-', '').replace(' ', '')

    def clean(self):
        cleaned_data = super().clean()
        
        # Nuevo paso de normalización
        self._normalize_rnc()
        
        validation_sequence = [
            self._normalize_na_values,
            self._validate_rnc_format,  # Validar después de normalizar
            self._validate_contact_methods,
            self._validate_unique_rnc_and_email
        ]
        
        for validation in validation_sequence:
            if not self.errors:
                validation()
            else:
                break

        return cleaned_data

    

    def _normalize_na_values(self):
        """Normalización de valores N/A con manejo de casos especiales"""
        na_fields = ['telefono', 'telefono2']
        
        for field in na_fields:
            value = self.cleaned_data.get(field, '')
            if value.upper() == self.NA_CHOICE:
                self.cleaned_data[field] = self.NA_CHOICE
                logger.debug(f"Campo {field} normalizado a N/A")

        # Validación especial para email
        email = self.cleaned_data.get('direccion_electronica', '')
        if email.upper() == self.NA_CHOICE:
            self.add_error(
                'direccion_electronica', 
                'El email no puede ser N/A - proporcione una dirección válida'
            )

    def save(self, commit=True):
        """Guardado con normalización adicional y registro detallado"""
        instance = super().save(commit=False)
        
        # Normalización final de datos
        instance.rnc = instance.rnc.strip()
        instance.direccion_electronica = instance.direccion_electronica.strip().lower()
        
        if commit:
            try:
                instance.save()
                logger.info(
                    f"Empresa {instance.pk} actualizada por {self.user}",
                    extra={'user': self.user, 'empresa': instance}
                )
            except Exception as e:
                logger.error(
                    f"Error guardando empresa: {str(e)}",
                    exc_info=True,
                    extra={'user': self.user, 'data': self.cleaned_data}
                )
                raise

        return instance

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
            
            # Validación y normalización de extensión
            name, ext = os.path.splitext(archivo.name)
            ext = ext.lower()
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            
            if ext not in allowed_extensions:
                raise forms.ValidationError('Formato de archivo no permitido')
            
            # Generar nombre único con extensión normalizada
            unique_name = f"{name}_{uuid.uuid4().hex[:6]}{ext}"
            archivo.name = unique_name
            
        return archivo

    def clean(self):
        cleaned_data = super().clean()
        # Asegurar que el campo subido_por sea manejado correctamente
        if 'subido_por' in self.errors:
            del self.errors['subido_por']
        return cleaned_data

class NotaEmpresaForm(forms.ModelForm):
    class Meta:
        model = NotaEmpresa
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Escribe una nueva nota...',
                'minlength': '10'
            })
        }
        error_messages = {
            'contenido': {
                'required': 'El contenido de la nota es obligatorio',
                'min_length': 'La nota debe tener al menos 10 caracteres'
            }
        }

    def clean_contenido(self):
        contenido = self.cleaned_data.get('contenido')
        if contenido and len(contenido.strip()) < 10:
            raise forms.ValidationError("La nota debe contener al menos 10 caracteres válidos")
        return contenido.strip()