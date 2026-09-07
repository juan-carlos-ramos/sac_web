"""
Formularios del sistema SAC WEB
Sistema de Administración de Condominio
"""

from django import forms
from nucleo.models import Inmueble, Proveedor, Factura, Gasto, Pago, DatosCondominio, PerfilUsuario


# =============================================================================
# FORMULARIO: Inmueble
# =============================================================================

class InmuebleForm(forms.ModelForm):
    """
    Formulario para crear y editar inmuebles.
    """
    class Meta:
        model = Inmueble
        fields = ['numero_apto', 'propietario', 'documento_identidad', 'email', 'telefono', 'alicuota', 'fecha_ingreso', 'notas']
        widgets = {
            'numero_apto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1A, 2B, PH-1'
            }),
            'propietario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del propietario'
            }),
            'documento_identidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: V-12345678, J-31215969-3'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 0424-232-43-85'
            }),
            'alicuota': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.05263158',
                'step': '0.00000001'
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Comentarios o notas adicionales',
                'rows': 3
            }),
        }
        labels = {
            'numero_apto': 'Número de Apartamento',
            'propietario': 'Propietario',
            'documento_identidad': 'Documento de Identidad (R.I.F. / C.I.)',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono de Contacto',
            'alicuota': 'Alícuota (decimal)',
            'fecha_ingreso': 'Fecha de Ingreso',
            'notas': 'Comentarios Adicionales',
        }
        help_texts = {
            'alicuota': 'Porcentaje de participación en gastos comunes (ej: 0.05263158 = 5.26%)',
            'fecha_ingreso': 'Desde cuándo participa en las facturas de condominio',
        }


# =============================================================================
# FORMULARIO: Proveedor
# =============================================================================

class ProveedorForm(forms.ModelForm):
    """
    Formulario para crear y editar proveedores.
    """
    class Meta:
        model = Proveedor
        fields = ['nombre', 'rif', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa o persona'
            }),
            'rif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'J-12345678-9'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0414-1234567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
        }


# =============================================================================
# FORMULARIO: Factura
# =============================================================================

class FacturaForm(forms.ModelForm):
    """
    Formulario para crear facturas (períodos de facturación).
    """
    class Meta:
        model = Factura
        fields = ['periodo']
        widgets = {
            'periodo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2026-01',
                'pattern': '[0-9]{4}-[0-9]{2}'
            }),
        }
        labels = {
            'periodo': 'Período (YYYY-MM)',
        }
        help_texts = {
            'periodo': 'Formato: YYYY-MM (ej: 2026-01 para enero 2026)',
        }


# =============================================================================
# FORMULARIO: Gasto
# =============================================================================

class GastoForm(forms.ModelForm):
    """
    Formulario para agregar gastos a una factura.
    """
    class Meta:
        model = Gasto
        fields = ['descripcion', 'monto', 'categoria', 'es_gasto_no_comun', 'inmueble_especifico']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del gasto'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'es_gasto_no_comun': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'inmueble_especifico': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'descripcion': 'Descripción',
            'monto': 'Monto (Bs)',
            'categoria': 'Categoría',
            'es_gasto_no_comun': '¿Es gasto no común?',
            'inmueble_especifico': 'Inmueble específico',
        }
        help_texts = {
            'es_gasto_no_comun': 'Marcar si este gasto aplica solo a un inmueble',
            'inmueble_especifico': 'Solo si es gasto no común',
        }


# =============================================================================
# FORMULARIO: Pago
# =============================================================================

class PagoForm(forms.ModelForm):
    """
    Formulario para registrar pagos de inmuebles.
    """
    class Meta:
        model = Pago
        fields = [
            'factura', 'inmueble', 'fecha_pago', 'monto_pagado', 
            'moneda', 'tasa_cambio', 'metodo_pago', 'referencia', 
            'comprobante', 'notas'
        ]
        widgets = {
            'factura': forms.Select(attrs={'class': 'form-control'}),
            'inmueble': forms.Select(attrs={'class': 'form-control'}),
            'fecha_pago': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'monto_pagado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00'
            }),
            'moneda': forms.Select(attrs={'class': 'form-control'}),
            'tasa_cambio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.0000',
                'step': '0.0001'
            }),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de referencia'
            }),
            'comprobante': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,application/pdf'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
        }
        labels = {
            'factura': 'Factura',
            'inmueble': 'Inmueble',
            'fecha_pago': 'Fecha de Pago',
            'monto_pagado': 'Monto Pagado',
            'moneda': 'Moneda',
            'tasa_cambio': 'Tasa de Cambio',
            'metodo_pago': 'Método de Pago',
            'referencia': 'Referencia',
            'comprobante': 'Comprobante',
            'notas': 'Notas',
        }
        help_texts = {
            'tasa_cambio': 'Solo si el pago es en USD',
            'referencia': 'Obligatorio para transferencias y pago móvil',
        }

    def clean_comprobante(self):
        comprobante = self.cleaned_data.get('comprobante')
        if comprobante and hasattr(comprobante, 'size'):
            # Límite de 5MB por archivo
            max_size_mb = 5
            if comprobante.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f"El comprobante no debe superar los {max_size_mb} MB.")
            
            # Validar extensión permitida
            extension = comprobante.name.split('.')[-1].lower() if '.' in comprobante.name else ''
            if extension not in ['jpg', 'jpeg', 'png', 'pdf']:
                raise forms.ValidationError("Solo se permiten archivos en formato JPG, PNG o PDF.")
        return comprobante


# =============================================================================
# FORMULARIO: Datos del Condominio
# =============================================================================

class DatosCondominioForm(forms.ModelForm):
    """
    Formulario para editar datos del condominio.
    """
    class Meta:
        model = DatosCondominio
        fields = ['nombre_condominio', 'rif', 'direccion', 'datos_bancarios', 'contacto_admin']
        widgets = {
            'nombre_condominio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre oficial del condominio'
            }),
            'rif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'J-12345678-9'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
            'datos_bancarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Información de cuenta bancaria'
            }),
            'contacto_admin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre y teléfono del administrador'
            }),
        }


# =============================================================================
# FORMULARIOS: Gestión de Usuarios
# =============================================================================

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.hashers import make_password


class CrearUsuarioForm(UserCreationForm):
    """
    Formulario para crear nuevos usuarios del sistema.
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        }),
        label='Nombre'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        }),
        label='Apellido'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        }),
        label='Correo Electrónico'
    )
    
    # Campos de seguridad
    pregunta_seguridad = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ¿Cuál es el nombre de tu primera mascota?'
        }),
        label='Pregunta de Seguridad',
        help_text='Pregunta secreta para recuperar la contraseña'
    )
    
    respuesta_seguridad = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Respuesta secreta',
            'autocomplete': 'new-password'
        }),
        label='Respuesta',
        help_text='Esta respuesta será necesaria si olvidas tu contraseña'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Es Administrador',
        help_text='Los administradores tienen acceso completo al sistema'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'groups', 'pregunta_seguridad', 'respuesta_seguridad']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario (sin espacios)'
            }),
            'groups': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'username': 'Nombre de Usuario',
            'groups': 'Roles / Grupos',
            'is_staff': 'Es Administrador (Permite ver usuarios y auditoría)',
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data['is_staff']
        
        if commit:
            user.save()
            # Crear perfil con preguntas de seguridad (hasheando la respuesta)
            PerfilUsuario.objects.create(
                usuario=user,
                pregunta_seguridad=self.cleaned_data['pregunta_seguridad'],
                respuesta_seguridad=make_password(self.cleaned_data['respuesta_seguridad'].strip().lower())
            )
        return user


class EditarUsuarioForm(forms.ModelForm):
    """
    Formulario para editar usuarios existentes.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'groups']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Usuario Activo',
            'is_staff': 'Es Administrador (Permite ver usuarios y auditoría)',
            'groups': 'Roles / Grupos',
        }
        help_texts = {
            'is_active': 'Desmarcar para desactivar el usuario sin eliminarlo',
            'is_staff': 'Los administradores tienen acceso completo al sistema',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email


class CambiarPasswordUsuarioForm(SetPasswordForm):
    """
    Formulario para que el administrador cambie la contraseña de un usuario.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nueva contraseña'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'})
        self.fields['new_password1'].label = 'Nueva Contraseña'
        self.fields['new_password2'].label = 'Confirmar Nueva Contraseña'


