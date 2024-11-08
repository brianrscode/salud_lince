from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    pass

class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=6, unique=True)
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()

class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=6, unique=True)
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
