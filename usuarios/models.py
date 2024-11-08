from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    pass

class Medico(models.Model):
    matricula = models.CharField(primary_key=True, max_length=6, unique=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()

class Paciente(models.Model):
    matricula = models.CharField(primary_key=True, max_length=6, unique=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
