from django import forms
from .models import HistorialMedico
import re

class HistorialMedicoForm(forms.ModelForm):
    class Meta:
        model = HistorialMedico
        fields = [
            'enfermedades_cronicas',
            'alergias',
            'medicamento_usado',
            'es_embarazada',
            'usa_drogas',
            'usa_cigarro',
            'ingiere_alcohol'
        ]

    def __init__(self, *args, **kwargs):
        usuario = kwargs.get('instance').paciente  # Obtener el paciente asociado al historial
        super().__init__(*args, **kwargs)

        # Si el paciente es hombre, ocultamos el campo "es_embarazada"
        if usuario and usuario.sexo == 'M':
            self.fields['es_embarazada'].widget = forms.HiddenInput()


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo', "id": "email"})
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña', "id": "password"})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        token_email = r'^((ib|im|ii|ie|isc|lg|am)[0-9]{6}@itsatlixco\.edu\.mx)|(^admin[0-9]@admin\.com)|^([0-9]{6}@itsatlixco\.edu\.mx)$'

        if not re.match(token_email, email):
            raise forms.ValidationError("Correo no válido.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        token_password = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&ñ_])[A-Za-z\d@$!%*#?&ñ_]{8,15}$'

        if not re.match(token_password, password):
            raise forms.ValidationError("Contraseña no válida.")
        return password


class BulkUserUploadForm(forms.Form):
    file = forms.FileField(label="Selecciona un archivo (.csv o .xls)")
