from django import forms
from .models import Consulta, SignosVitales

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            'padecimiento_actual',
            'tratamiento_no_farmacologico',
            'tratamiento_farmacologico_recetado',
            'tipo_de_consulta',
            'clave_paciente'
        ]
        widgets = {
            'padecimiento_actual': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'tratamiento_no_farmacologico': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tratamiento_farmacologico_recetado': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tipo_de_consulta': forms.Select(attrs={'class': 'form-select'}),
            'clave_paciente': forms.Select(attrs={'class': 'form-select'}),
        }

class SignosVitalesForm(forms.ModelForm):
    class Meta:
        model = SignosVitales
        fields = [
            'peso',
            'talla',
            'temperatura',
            'frecuencia_cardíaca',
            'frecuencia_respiratoria',
            'presion_arterial'
        ]
        widgets = {
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'talla': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_cardíaca': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_respiratoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'presion_arterial': forms.TextInput(attrs={'class': 'form-control'}),
        }
