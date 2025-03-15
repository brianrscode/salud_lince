from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password


class UsuarioManager(BaseUserManager):
    def create_user(self, clave, nombres, email, apellido_paterno, fecha_nacimiento, sexo=None, apellido_materno=None, password=None, role=None, carrera_o_puesto=None):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')

        # if not password or len(password) < 8:
        #     raise ValueError('La contraseña debe tener al menos 8 caracteres')

        # Asignar el rol por defecto si no se proporciona uno
        if role is None:
            role = Role.objects.get(nombre_rol='paciente')

        # Buscar role y carrera
        try:
            role_obj = Role.objects.get(nombre_rol=role)
        except ObjectDoesNotExist:
            raise ValueError(f"El rol {role} no existe")

        try:
            carrera_o_puesto_obj = Area.objects.get(carrera_o_puesto=carrera_o_puesto)
        except ObjectDoesNotExist:
            raise ValueError(f"La carrera o puesto {carrera_o_puesto} no existe")

        usuario = self.model(
            clave=clave,
            nombres=nombres,
            email=self.normalize_email(email),
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            role=role_obj,
            carrera_o_puesto=carrera_o_puesto_obj
        )
        usuario.set_password(password)  # Hashea la contraseña
        usuario.save(using=self._db)

        return usuario


    def create_superuser(self, clave, nombres, email, apellido_paterno=None, apellido_materno=None, fecha_nacimiento=None, sexo=None, password=None, role="admin", carrera_o_puesto="Administración"):
        usuario = self.create_user(
            clave=clave,
            nombres=nombres,
            email=email,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            password=password,
            role=role,
            carrera_o_puesto=carrera_o_puesto
        )
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


class Area(models.Model):
    carrera_o_puesto = models.CharField(max_length=50, unique=True, primary_key=True)

    def __str__(self):
        return self.carrera_o_puesto


class Role(models.Model):
    nombre_rol = models.CharField(max_length=20, unique=True, primary_key=True)
    descripcion = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nombre_rol


class Usuario(AbstractBaseUser, PermissionsMixin):
    clave = models.CharField('clave', max_length=9, primary_key=True, unique=True,
                             validators=[RegexValidator(
                                 regex=r'^((ib|im|ii|ie|isc|lg|am)[0-9]{6})|^(admin[0-9])|^([0-9]{6})$',
                                 message='Formato de clave no valido'
                             )])
    email = models.EmailField('Correo', unique=True,
                              validators=[RegexValidator(
                                  regex=r'^((ib|im|ii|ie|isc|lg|am)[0-9]{6}@itsatlixco\.edu\.mx)|(^admin[0-9]@admin\.com)|^([0-9]{6}@itsatlixco\.edu\.mx)$',
                                  message='Formato de correo no valido'
                              )])
    nombres = models.CharField('Nombres', max_length=100,
                               validators=[RegexValidator(r'^([A-ZÑÁÉÍÓÚ][a-zñáéíóú]+)( [A-ZÑÁÉÍÓÚ][a-zñáéíóú]+)?$')])
    apellido_paterno = models.CharField('Apellido Paterno', max_length=30,
                                        validators=[RegexValidator(r'^[A-ZÑÁÉÍÓÚ][a-zñáéíóú]+')])
    apellido_materno = models.CharField('Apellido Materno', max_length=30, blank=True, null=True,
                                        validators=[RegexValidator(r'^[A-ZÑÁÉÍÓÚ][a-zñáéíóú]+')])
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', blank=True, null=True)
    sexos = [('M', 'Masculino'), ('F', 'Femenino')]
    sexo = models.CharField('Sexo', max_length=1, choices=sexos, blank=True, null=True)
    is_active = models.BooleanField("Usuario activo", default=True)
    is_staff = models.BooleanField(default=False)

    carrera_o_puesto = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['clave', 'nombres', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento']

    # Validador para la contraseña, asegura que tenga al menos 8 caracteres
    password_validator = RegexValidator(
        regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&ñ_])[A-Za-z\d@$!%*#?&ñ_]{8,15}$',
        message='La contraseña debe tener al entre 8 y 15 caracteres, incluir una letra mayúscula, un número y un caracter especial.'
    )

    password = models.CharField(
        'Contraseña',
        max_length=128,
        validators=[password_validator],
        blank=False
    )

    def save(self, *args, **kwargs):
        """ Sobrescribe el método save() para garantizar que la contraseña se guarde cifrada. """
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)

        if self.role is None:
            self.role = Role.objects.get(nombre_rol='paciente')

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.clave} - {self.nombres} - {self.role}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class HistorialMedico(models.Model):
    id_historial = models.CharField('Id Historial', max_length=9, primary_key=True, unique=True, editable=False)
    enfermedades_cronicas = models.CharField('Enfermedades crónicas', max_length=150, blank=True, null=True)
    alergias = models.CharField('Alergias', max_length=150, blank=True, null=True)
    medicamento_usado = models.CharField('Medicamento usado', max_length=150, blank=True, null=True)
    es_embarazada = models.BooleanField(default=False)
    usa_drogas = models.BooleanField(default=False)
    usa_cigarro = models.BooleanField(default=False)
    ingiere_alcohol = models.BooleanField(default=False)
    usa_lentes = models.BooleanField(default=False)
    vida_sexual_activa = models.BooleanField(default=False)
    usa_metodos_anticonceptivos = models.BooleanField("Usa métodos anticonceptivos", default=False)

    paciente = models.OneToOneField('Usuario', on_delete=models.CASCADE, related_name='historial', null=True, editable=False)

    def __str__(self):
        return f'{self.id_historial}'
