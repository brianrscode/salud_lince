from django import forms
from .models import Consulta, SignosVitales
from usuarios.models import Usuario

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            'padecimiento_actual',
            'tratamiento_no_farmacologico',
            'tratamiento_farmacologico_recetado',
            'categoria_de_padecimiento',
            'clave_paciente'
        ]
        widgets = {
            'padecimiento_actual': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'tratamiento_no_farmacologico': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tratamiento_farmacologico_recetado': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'categoria_de_padecimiento ': forms.Select(attrs={'class': 'form-select'}),
            'clave_paciente': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo pacientes en el queryset
        self.fields['clave_paciente'].queryset = Usuario.objects.filter(role__nombre_rol='paciente')

class SignosVitalesForm(forms.ModelForm):
    class Meta:
        model = SignosVitales
        fields = [
            'peso',
            'talla',
            'temperatura',
            'frecuencia_cardiaca',
            'frecuencia_respiratoria',
            'presion_arterial'
        ]
        widgets = {
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'talla': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_respiratoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'presion_arterial': forms.TextInput(attrs={'class': 'form-control'}),
        }
