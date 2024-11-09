from django.db import models
from usuarios.models import Usuario


class Consulta(models.Model):
    id_consulta = models.AutoField(primary_key=True, unique=True, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)
    padecimiento_actual = models.TextField()
    tratamiento_no_farmacologico = models.TextField('Tratamiento no farmacológico', max_length=100, blank=True, null=True)
    tratamiento_farmacologico = models.CharField('Tratamiento farmacológico', max_length=100, blank=True, null=True)
    peso = models.DecimalField('Peso (kg)', max_digits=3, decimal_places=1, blank=True, null=True)  # en kg
    talla = models.DecimalField('Talla (m)', max_digits=3, decimal_places=1, blank=True, null=True)  # en cm
    temperatura = models.DecimalField('Temperatura (°C)', max_digits=2, decimal_places=1, blank=True, null=True)  # en °C
    frecuencia_cardíaca = models.IntegerField('Frecuencia cardíaca (bpm)', blank=True, null=True)  # en bpm
    frecuencia_respiratoria = models.IntegerField('Frecuencia respiratoria (rpm)', blank=True, null=True)  # en rpm
    presion_arterial = models.CharField('Presión arterial', max_length=7, blank=True, null=True)  # ej: "120/80"
    matricula_paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultas_paciente',
        limit_choices_to={'role': 'paciente'}
    )
    paciente_medico = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultas_medico',
        limit_choices_to={'role': 'medico'}
    )

    def __str__(self):
        return f"Consulta {self.id_consulta} - {self.fecha} - {self.matricula_paciente} - {self.paciente_medico}"
