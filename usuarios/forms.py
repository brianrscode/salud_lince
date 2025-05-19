import re

from django import forms

from .models import HistorialMedico

class HistorialMedicoForm(forms.ModelForm):
    """
    Formulario para el modelo HistorialMedico.
    Este formulario personaliza el comportamiento del campo `es_embarazada`:
    Si el paciente es hombre (sexo == 'M'), el campo se oculta automáticamente
    al renderizar el formulario.

    Utiliza todos los campos del modelo por defecto.
    """
    class Meta:
        model = HistorialMedico
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        usuario = kwargs.get('instance').paciente  # Obtener el paciente asociado al historial
        super().__init__(*args, **kwargs)

        # Si el paciente es hombre, ocultamos el campo "es_embarazada"
        if usuario and usuario.sexo == 'M':
            self.fields['es_embarazada'].widget = forms.HiddenInput()


class LoginForm(forms.Form):
    """
    Formulario personalizado de inicio de sesión.
    Este formulario solicita dos campos:
    - clave: Identificador institucional o de administrador.
    - password: Contraseña segura con validación de complejidad.

    Ambos campos se validan mediante expresiones regulares.
    """
    clave = forms.CharField(
        label='Clave',
        max_length=9,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clave', "id": "clave"})
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña', "id": "password"})
    )

    def clean_clave(self):
        """
        Valida que la clave ingresada cumpla con el formato requerido.
        Formatos válidos:
        - Estudiantes o docentes (ej. ib123456)
        - Administradores (ej. admin1)
        - Claves numéricas simples (ej. 1234)

        Raises:
            ValidationError: Si la clave no cumple con el formato.
        Returns:
            str: Clave validada.
        """
        clave = self.cleaned_data.get('clave')
        if not str(clave).startswith('admin'):
            clave = clave.upper()
        token_clave = r'^((IB|IM|II|IE|ISC|LG|AM)[0-9]{4,6})|^(admin[0-9])|^([0-9]{4,6})$'

        if not re.match(token_clave, clave):
            raise forms.ValidationError("Ingrese su matrícula o número de trabajador.")
        return clave

    def clean_password(self):
        """
        Valida que la contraseña tenga al menos:
        - Una letra mayúscula
        - Una letra minúscula
        - Un número
        - Un carácter especial
        - Longitud entre 8 y 15 caracteres

        Raises:
            ValidationError: Si la contraseña no cumple con los requisitos.
        Returns:
            str: Contraseña validada.
        """
        password = self.cleaned_data.get('password')
        token_password = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&ñ_])[A-Za-z\d@$!%*#?&ñ_]{8,15}$'

        if not re.match(token_password, password):
            raise forms.ValidationError("Contraseña no válida.")
        return password


class BulkUserUploadForm(forms.Form):
    """
    Formulario para la carga masiva de usuarios mediante archivo.
    Este formulario permite al administrador seleccionar un archivo `.csv` o `.xls`
    que contenga los datos de múltiples usuarios para ser procesados e importados
    al sistema.

    """
    file = forms.FileField(label="Selecciona un archivo (.csv o .xls)")
