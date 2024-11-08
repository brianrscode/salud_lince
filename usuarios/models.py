from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    # Campos extras
    telefono = models.CharField(max_length=10, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino')], blank=True)

    # Tipo de usuario
    TIPO_USUARIO_CHOICES = [
        ('doctor', 'Doctor'),
        ('paciente', 'Paciente'),
    ]
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)

    def __str__(self):
        return f"{self.username} - {self.tipo_usuario}"
