import re

from django import forms

from .models import HistorialMedico

class HistorialMedicoForm(forms.ModelForm):
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
        clave = self.cleaned_data.get('clave')
        token_clave = r'^((ib|im|ii|ie|isc|lg|am)[0-9]{4,6})|^(admin[0-9])|^([0-9]{4,6})$'

        if not re.match(token_clave, clave):
            raise forms.ValidationError("Clave no válida.")
        return clave

    def clean_password(self):
        password = self.cleaned_data.get('password')
        token_password = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&ñ_])[A-Za-z\d@$!%*#?&ñ_]{8,15}$'

        if not re.match(token_password, password):
            raise forms.ValidationError("Contraseña no válida.")
        return password


class BulkUserUploadForm(forms.Form):
    file = forms.FileField(label="Selecciona un archivo (.csv o .xls)")
