from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from usuarios.decorators import role_required
from usuarios.models import Usuario

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
    # Crear las instancias de los formularios con los datos enviados
    consulta_form = ConsultaForm(data=request.POST or None)
    signos_form = SignosVitalesForm(data=request.POST or None)

    # Si el método es POST (es decir, el usuario está enviando el formulario)
    if request.method == 'POST':
        # Validar ambos formularios
        if consulta_form.is_valid() and signos_form.is_valid():
            clave = request.POST.get('clave_paciente_display').split('-')[0].strip()
            try:
                paciente = Usuario.objects.get(clave=clave, role__nombre_rol='paciente', is_active=True)
            except Usuario.DoesNotExist:
                messages.error(request, 'No se encontró un paciente con esa clave.')
                return redirect('crear_consulta')

            consulta = consulta_form.save(commit=False)
            consulta.clave_medico = request.user
            consulta.clave_paciente = paciente
            consulta.save()

            signos_vitales = signos_form.save(commit=False)
            signos_vitales.consulta = consulta
            signos_vitales.save()

            messages.success(request, 'Consulta registrada correctamente.')
            return redirect('medico_consultas')
        else:
            # Si los formularios no son válidos, mostrar un mensaje de error
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    # Si el método no es POST, solo mostrar los formularios vacíos

    # Renderizar la plantilla con los formularios
    return render(request, 'crear_consulta.html', {
        'consulta_form': consulta_form,
        'signos_form': signos_form
    })


@csrf_exempt
@never_cache
@login_required
@role_required(['medico'])
def buscar_paciente_por_clave(request):
    clave = request.GET.get('clave', '').lower()
    try:
        paciente = Usuario.objects.get(clave__iexact=clave, role__nombre_rol='paciente', is_active=True)
        return JsonResponse({'encontrado': True, 'clave': paciente.clave, 'nombre': paciente.nombres})
    except Usuario.DoesNotExist:
        return JsonResponse({'encontrado': False})


frecuencia_cardiaca_temporal = {} # Diccionario para almacenar temporalmente la frecuencia

@csrf_exempt # Necesario para peticiones POST desde fuera del formulario de Django
def recibir_frecuencia(request):
    if request.method == 'POST':
        try:
            frecuencia = request.POST.get('frecuencia_cardiaca')
            # Aquí podrías implementar lógica para identificar la consulta o el médico
            # Por ahora, simplemente almacenamos la última frecuencia recibida
            frecuencia_cardiaca_temporal['ultima_lectura'] = frecuencia
            return JsonResponse({'status': 'success', 'mensaje': 'Frecuencia cardíaca recibida'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_ultima_frecuencia(request):
    if 'ultima_lectura' in frecuencia_cardiaca_temporal:
        frecuencia = frecuencia_cardiaca_temporal['ultima_lectura']
        return JsonResponse({'frecuencia_cardiaca': frecuencia})
    else:
        return JsonResponse({'frecuencia_cardiaca': None})