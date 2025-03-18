from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, 
    UserCreationForm, 
    SetPasswordForm
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from .models import UsuarioPersonalizado
from .models import CompanySettings

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Usuario'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nombre de usuario'),
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )

    error_messages = {
        'invalid_login': _(
            "Credenciales inválidas. Por favor verifique sus datos."
        ),
        'inactive': _("Esta cuenta está inactiva."),
        'no_admin_privileges': _("No tiene permisos para acceder a este sistema."),
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        # Eliminar la restricción de rol
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('correo@ejemplo.com')
        })
    )
    
    class Meta:
        model = UsuarioPersonalizado
        fields = ('username', 'email', 'rol', 'is_staff', 'telefono')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_staff': _('Acceso al Admin'),
            'rol': _('Rol del usuario'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden"))
        
        validate_password(password2, self.instance)
        return password2

class AdminPasswordChangeForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("Nueva contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        }),
    )
    new_password2 = forms.CharField(
        label=_("Confirmar nueva contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = None

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden"))
        
        validate_password(password2, self.user)
        return password2
    
class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = ['logo']
        labels = {
            'logo': _('Seleccionar nuevo logo')
        }
        help_texts = {
            'logo': _('Formatos aceptados: PNG, JPG, JPEG, SVG. Preferible PNG con fondo transparente (400x150 px)')
        }
        widgets = {
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }