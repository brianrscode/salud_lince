import re

from django import forms
from datetime import date
from apps.usuarios.models import Usuario
from apps.usuarios.models import HistorialMedico

class HistorialMedicoForm(forms.ModelForm):
    """
    Formulario para el modelo HistorialMedico.
    Este formulario personaliza el comportamiento del campo `es_embarazada`:
    Si el paciente es hombre (sexo == 'M'), el campo se oculta automáticamente
    al renderizar el formulario.

    Utiliza todos los campos del modelo por defecto.
    """
    class Meta:
        model = HistorialMedico
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        usuario = kwargs.get('instance').paciente  # Obtener el paciente asociado al historial
        super().__init__(*args, **kwargs)

        # Si el paciente es hombre, ocultamos el campo "es_embarazada"
        if usuario and usuario.sexo == 'M':
            self.fields['es_embarazada'].widget = forms.HiddenInput()


class LoginForm(forms.Form):
    """
    Formulario personalizado de inicio de sesión.
    Este formulario solicita dos campos:
    - clave: Identificador institucional o de administrador.
    - password: Contraseña segura con validación de complejidad.

    Ambos campos se validan mediante expresiones regulares.
    """
    clave = forms.CharField(
        label='Clave',
        max_length=9,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clave', "id": "clave"})
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña', "id": "password"})
    )

    def clean_clave(self):
        """
        Valida que la clave ingresada cumpla con el formato requerido.
        Formatos válidos:
        - Estudiantes o docentes (ej. ib123456)
        - Administradores (ej. admin1)
        - Claves numéricas simples (ej. 1234)

        Raises:
            ValidationError: Si la clave no cumple con el formato.
        Returns:
            str: Clave validada.
        """
        clave = self.cleaned_data.get('clave')
        if not str(clave).startswith('admin'):
            clave = clave.upper()
        token_clave = r'^((AM|BIE|BIS|BLG|BII|BIM|BIB|CLG|CIM|CIE|CII|CIB|IB|IE|II|IM|ISC|LG|MI|MXI|MXM|MXE|MXS|MIA)[0-9]{4,6})|^(admin[0-9])|^([0-9]{4,6})$'

        if not re.match(token_clave, clave):
            raise forms.ValidationError("Ingrese su matrícula o número de trabajador.")
        return clave

    def clean_password(self):
        """
        Valida que la contraseña tenga al menos:
        - Una letra mayúscula
        - Una letra minúscula
        - Un número
        - Un carácter especial
        - Longitud entre 8 y 15 caracteres

        Raises:
            ValidationError: Si la contraseña no cumple con los requisitos.
        Returns:
            str: Contraseña validada.
        """
        password = self.cleaned_data.get('password')
        token_password = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&ñ_])[A-Za-z\d@$!%*#?&ñ_]{8,15}$'

        if not re.match(token_password, password):
            raise forms.ValidationError("Contraseña inválida.")
        return password


class BulkUserUploadForm(forms.Form):
    """
    Formulario para la carga masiva de usuarios mediante archivo.
    Este formulario permite al administrador seleccionar un archivo `.csv` o `.xls`
    que contenga los datos de múltiples usuarios para ser procesados e importados
    al sistema.

    """
    file = forms.FileField(label="Selecciona un archivo (.csv o .xls)")


class ValidarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define el formato aceptado para la entrada
        self.fields['fecha_nacimiento'].input_formats = ['%d/%m/%Y']

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > date.today():
            raise forms.ValidationError("La fecha de nacimiento no válida.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()

        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        clave = cleaned_data.get('clave', '')
        carrera = cleaned_data.get('carrera_o_puesto')
        rol = cleaned_data.get('role')

        errores = []
        edad = None

        # 🔹 Calcula edad
        if fecha_nacimiento:
            edad = date.today().year - fecha_nacimiento.year
            if (date.today().month, date.today().day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                edad -= 1
        if rol and rol.nombre_rol == 'paciente' and edad is not None and edad < 15:
            self.add_error('fecha_nacimiento', "Fecha de nacimiento no válida.")

        # 🔹 Validación de coherencia entre rol y carrera
        if rol:
            if rol.nombre_rol.lower() == "medico" and carrera and carrera.carrera_o_puesto != "Médico":
                self.add_error('carrera_o_puesto', "El rol Médico solo puede pertenecer al área Médica.")
            elif rol.nombre_rol.lower() == "administrador" and carrera and carrera.carrera_o_puesto != "ADMINISTRATIVO":
                self.add_error('carrera_o_puesto', "El rol Administrador debe pertenecer al área Administrativo.")

        # 🔹 Validación de clave y área
        if clave.startswith("II") and carrera and "INDUSTRIAL" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'II' corresponde a Ingeniería Industrial.")
        elif clave.startswith("ISC") and carrera and "SISTEMAS" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'ISC' corresponde a Ingeniería en Sistemas Computacionales.")
        elif clave.startswith("IM") and carrera and "MECATRÓNICA" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'IM' corresponde a Ingeniería Mecatrónica.")
        elif clave.startswith("IB") and carrera and "BIOQUÍMICA" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'IB' corresponde a Ingeniería Bioquímica.")
        elif clave.startswith("IE") and carrera and "ELECTROMECÁNICA" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'IE' corresponde a Ingeniería Electromecánica.")
        elif clave.startswith("LG") and carrera and "GASTRONOMÍA" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'LG' corresponde a Licenciatura en Gastronomía.")
        elif clave.startswith("MI") and carrera and "M. EN INGENIERÍA" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'MI' corresponde a la Maestría en Ingeniería")
        elif clave.startswith("MIA") and carrera and "MAESTRÍA EN IA" not in carrera.carrera_o_puesto.upper():
            self.add_error('clave', "La clave 'MIA' corresponde a MAESTRÍA en IA.")
        # elif clave.startswith("am") and carrera and "MÉDICO" not in carrera.carrera_o_puesto.upper():
        #   self.add_error('clave', "La clave 'am' corresponde al área Médica.")

        return cleaned_data
