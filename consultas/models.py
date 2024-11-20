from django.db import models
from usuarios.models import Usuario


class Consulta(models.Model):
    id_consulta = models.BigAutoField(primary_key=True)
    fecha = models.DateField(auto_now_add=True)
    padecimiento_actual = models.TextField()
    tratamiento_no_farmacologico = models.TextField('Tratamiento no farmacológico', max_length=100, blank=True, null=True)
    tratamiento_farmacologico_recetado = models.CharField('Tratamiento farmacológico recetado', max_length=100, blank=True, null=True)
    CHOICES = [("M", "Médica"), ("A", "Asesoría")]
    tipo_de_consulta = models.CharField('Tipo de consulta', max_length=1, choices=CHOICES, default="M")
    clave_paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultas_paciente',
        limit_choices_to={'role__nombre_rol': 'paciente'}
    )
    paciente_medico = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultas_medico',
        limit_choices_to={'role__nombre_rol': 'medico'}
    )

    def __str__(self):
        return f"Consulta {self.id_consulta} - {self.fecha} - {self.clave_paciente} - {self.paciente_medico}"


class SignosVitales(models.Model):
    id_signos = models.BigAutoField(primary_key=True)
    peso = models.DecimalField('Peso (kg)', max_digits=4, decimal_places=2, blank=True, null=True)  # en kg
    talla = models.DecimalField('Talla (m)', max_digits=4, decimal_places=2, blank=True, null=True)  # en cm
    temperatura = models.DecimalField('Temperatura (°C)', max_digits=4, decimal_places=2, blank=True, null=True)  # en °C
    frecuencia_cardíaca = models.IntegerField('Frecuencia cardíaca (bpm)', blank=True, null=True)  # en bpm
    frecuencia_respiratoria = models.IntegerField('Frecuencia respiratoria (rpm)', blank=True, null=True)  # en rpm
    presion_arterial = models.CharField('Presión arterial', max_length=7, blank=True, null=True)  # ej: "120/80"

    consulta = models.OneToOneField(
        'Consulta',
        on_delete=models.CASCADE,
        related_name='signos_vitales'
    )

    def __str__(self):
        return f"{self.id_signos} - {self.consulta}"