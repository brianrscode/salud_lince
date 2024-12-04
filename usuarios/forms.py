from django import forms
from .models import HistorialMedico

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
