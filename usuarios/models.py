from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsuarioManager(BaseUserManager):
    def create_user(self, matricula, nombres, email, password=None, role=None):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')

        usuario = self.model(
            matricula=matricula,
            nombres=nombres,
            email=self.normalize_email(email),
            role=role
        )
        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario

    def create_superuser(self, matricula, nombres, email, password=None):
        usuario = self.create_user(
            matricula=matricula,
            nombres=nombres,
            email=email,
            password=password,
            role='admin'
        )
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario



class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('medico', 'Médico'),
        ('paciente', 'Paciente'),
        ('admin', 'Administrador'),
    )

    matricula = models.CharField('Matrícula', max_length=9, primary_key=True, unique=True)
    email = models.EmailField('Correo', unique=True)
    nombres = models.CharField('Nombres', max_length=100)
    apellido_paterno = models.CharField('Apellido Paterno', max_length=30)
    apellido_materno = models.CharField('Apellido Materno', max_length=30, blank=True, null=True)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', blank=True, null=True)
    usuario_activo = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='paciente')

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['matricula', 'nombres']

    def __str__(self):
        return f'{self.matricula} - {self.nombres} - {self.role}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class HistorialMedico(models.Model):
    id_historial = models.CharField('Id Historial', max_length=9, primary_key=True, unique=True)
    enfermedades_cronicas = models.CharField('Enfermedades crónicas', max_length=150, blank=True, null=True)
    alergias = models.CharField('Alergias', max_length=150, blank=True, null=True)
    medicamento_usado = models.CharField('Medicamento usado', max_length=150, blank=True, null=True)
    es_embarazada = models.BooleanField(default=False)
    usa_drogas = models.BooleanField(default=False)
    usa_cigarro = models.BooleanField(default=False)
    ingiere_alcohol = models.BooleanField(default=False)

    paciente = models.OneToOneField('Usuario', on_delete=models.CASCADE, related_name='historial', null=True, editable=False)

    def __str__(self):
        return f'{self.id_historial}'

