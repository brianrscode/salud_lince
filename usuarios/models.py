from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsuarioManager(BaseUserManager):
    def create_user(self, clave, nombres, email, apellido_paterno, fecha_nacimiento, apellido_materno=None, password=None, role=None):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')

        try:
            role_obj = Role.objects.get(nombre_rol=role)
        except ObjectDoesNotExist:
            raise ValueError(f"El rol {role} no existe")

        usuario = self.model(
            clave=clave,
            nombres=nombres,
            email=self.normalize_email(email),
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
            role=role_obj
        )
        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario

    def create_superuser(self, clave, nombres, email, apellido_paterno=None, apellido_materno=None, fecha_nacimiento=None, password=None, role="admin"):
        try:
            role_obj = Role.objects.get(nombre_rol=role)
        except ObjectDoesNotExist:
            raise ValueError(f"El rol {role} no existe")
        usuario = self.create_user(
            clave=clave,
            nombres=nombres,
            email=email,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
            password=password,
            role=role_obj
        )
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


class Role(models.Model):
    nombre_rol = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nombre_rol


class Usuario(AbstractBaseUser, PermissionsMixin):

    clave = models.CharField('clave', max_length=9, primary_key=True, unique=True)
    email = models.EmailField('Correo', unique=True)
    nombres = models.CharField('Nombres', max_length=100)
    apellido_paterno = models.CharField('Apellido Paterno', max_length=30)
    apellido_materno = models.CharField('Apellido Materno', max_length=30, blank=True, null=True)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', blank=True, null=True)
    usuario_activo = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=0)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['clave', 'nombres', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento']

    def __str__(self):
        return f'{self.clave} - {self.nombres} - {self.role}'

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

