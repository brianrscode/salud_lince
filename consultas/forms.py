import re
from django.core.exceptions import ValidationError
from django import forms
from usuarios.models import Usuario
from .models import Consulta, SignosVitales

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            'clave_paciente',
            'padecimiento_actual',
            'tratamiento_no_farmacologico',
            'tratamiento_farmacologico_recetado',
            'categoria_de_padecimiento',
        ]
        widgets = {  # Ajustar widgets para cada campo con estilo de Bootstrap
            'clave_paciente': forms.Select(attrs={'class': 'form-select'}),
            'padecimiento_actual': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'tratamiento_no_farmacologico': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tratamiento_farmacologico_recetado': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'categoria_de_padecimiento ': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo pacientes en el queryset
        self.fields['clave_paciente'].queryset = Usuario.objects.filter(
            role__nombre_rol='paciente',
            is_active=True
        ).only('clave')

class SignosVitalesForm(forms.ModelForm):
    class Meta:
        model = SignosVitales
        exclude = ['id_signos', 'consulta']
        widgets = {
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'talla': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_respiratoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'presion_arterial': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        if peso is not None and not re.match(r'^(?:[4-9][0-9]|1[0-9][0-9])(?:\.[0-9])?$', str(peso)):
            raise ValidationError('Dato no valido (ejemplo de dato a ingresar: "40.0-199.9")')
        return peso

    def clean_talla(self):
        talla = self.cleaned_data.get('talla')
        if talla is not None and not re.match(r'^(1\.\d{1,2}|2\.[0-2]\d?)$', str(talla)):
            raise ValidationError('Dato no valido (ejemplo de dato a ingresar: "1.00-2.29")')
        return talla

    def clean_temperatura(self):
        temperatura = self.cleaned_data.get('temperatura')
        if temperatura is not None and not re.match(r'^(3[5-9]|4[0-3])(\.[0-9])?$', str(temperatura)):
            raise ValidationError('Dato no valido no valido (ejemplo de dato a ingresar: "35.0-43.9")')
        return temperatura

    def clean_frecuencia_cardiaca(self):
        fc = self.cleaned_data.get('frecuencia_cardiaca')
        if fc is not None and not re.match(r'^(5[0-9]|[6-9][0-9]|100)$', str(fc)):
            raise ValidationError('Dato no valido (ejemplo de dato a ingresar: "50-100")')
        return fc

    def clean_frecuencia_respiratoria(self):
        fr = self.cleaned_data.get('frecuencia_respiratoria')
        if fr is not None and not re.match(r'^(12|1[3-9]|2[0-9]|3[0-9]|40)$', str(fr)):
            raise ValidationError('Dato no valido (ejemplo de dato a ingresar: "12-40")')
        return fr

    def clean_presion_arterial(self):
        pa = self.cleaned_data.get('presion_arterial')
        if pa and not re.match(r'^(1[01][0-9]|120|12[0-9]|1[3-9][0-9]|140)/(60|6[0-9]|70|7[0-9]|80|8[0-9]|90)$', pa):
            raise ValidationError('Dato no valido (ejemplo de dato a ingresar: "120/80")')
        return pa