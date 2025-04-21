from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from usuarios.decorators import role_required

from .forms import ConsultaForm, SignosVitalesForm


@never_cache
@login_required
@role_required(['medico'])
def crear_consulta(request):
    """
    Vista para crear una nueva consulta médica y registrar los signos vitales del paciente.
    Solo accesible para usuarios con el rol de 'medico'.
    """
    # Verificar si el usuario tiene el rol 'medico'. Si no, redirigir al dashboard con un mensaje de error.
    if not request.user.role.nombre_rol == 'medico':
        messages.error(request, 'Solo los médicos pueden crear consultas.')
        return redirect('dashboard')

    # Si el método es POST (es decir, el usuario está enviando el formulario)
    if request.method == 'POST':
        # Crear las instancias de los formularios con los datos enviados
        consulta_form = ConsultaForm(request.POST)
        signos_form = SignosVitalesForm(request.POST)

        # Validar ambos formularios
        if consulta_form.is_valid() and signos_form.is_valid():
            # Si ambos formularios son válidos, proceder con la creación de los objetos
            # Guardar la consulta, pero no la comiteamos todavía
            consulta = consulta_form.save(commit=False)
            consulta.clave_medico = request.user  # Asignar el médico autenticado a la consulta
            consulta.save()  # Guardar la consulta en la base de datos

            # Guardar los signos vitales relacionados con la consulta
            signos_vitales = signos_form.save(commit=False)
            signos_vitales.consulta = consulta  # Asociar los signos vitales con la consulta
            signos_vitales.save()  # Guardar los signos vitales en la base de datos

            # Mostrar un mensaje de éxito y redirigir al listado de consultas del médico
            messages.success(request, 'La consulta y los signos vitales fueron creados exitosamente.')
            return redirect('medico_consultas')
        else:
            # Si los formularios no son válidos, mostrar un mensaje de error
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    # Si el método no es POST, solo mostrar los formularios vacíos
    else:
        consulta_form = ConsultaForm()
        signos_form = SignosVitalesForm()

    # Renderizar la plantilla con los formularios
    return render(request, 'crear_consulta.html', {
        'consulta_form': consulta_form,
        'signos_form': signos_form
    })
