from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from consultas.models import Consulta, SignosVitales
from .models import HistorialMedico
from django.forms.models import ModelForm


def login_view(request):
    # Si ya hay una sesión iniciada, redirigir al dashboard del rol correspondiente
    if request.user.is_authenticated:
        if request.user.role.nombre_rol == "medico":
            return redirect("medico_dashboard")  # Nombre de la vista para médicos
        elif request.user.role.nombre_rol == "paciente":
            return redirect("paciente_dashboard")  # Nombre de la vista para pacientes

    if request.method == "POST":
        ''' Si el formulario es enviado se autentica el usuario '''
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            # Redirigir según el rol del usuario
            if user.role.nombre_rol == "medico":
                return redirect("medico_dashboard")  # Nombre de la vista para médicos
            elif user.role.nombre_rol == "paciente":
                return redirect("paciente_dashboard")  # Nombre de la vista para pacientes
            elif user.role.nombre_rol == "admin":
                return redirect("/admin/")
            else:
                messages.error(request, "Rol no reconocido.")
                return redirect("login")
        else:
            messages.error(request, "Credenciales inválidas.")
    return render(request, "login.html")


def logout_view(request):
    # if request.user.is_authenticated:
    logout(request)
    return redirect("login")


@login_required
@role_required(["medico"])
def medico_dashboard(request):
    return render(request, "medico_dashboard.html")


@login_required
@role_required(["paciente"])
def paciente_dashboard(request):
    return render(request, "paciente_dashboard.html")


@login_required
@role_required(["paciente"])
def historial_view(request):
    # obtener el historial médico del paciente
    historial = request.user.historial
    return render(request, "historial_medico.html", {"historial": historial})


@login_required
@role_required(["paciente"])
def paciente_consultas(request):
    consultas = Consulta.objects.filter(clave_paciente=request.user)
    signos = SignosVitales.objects.filter(consulta__clave_paciente=request.user)
    return render(request, "paciente_consultas.html", {"consultas": consultas, "signos": signos})


@login_required
@role_required(["paciente", "medico"])
def usuario_informacion(request):
    informacion = request.user
    return render(request, "informacion.html", {"informacion": informacion})


@login_required
@role_required(["paciente", "medico"])
def cambiar_contrasena(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            error_message = 'La contraseña actual es incorrecta.'
            return render(request, "informacion.html", {
                'informacion': request.user,
                'error': error_message
            })

        if new_password != confirm_password:
            error_message = 'Las contraseñas no coinciden.'
            return render(request, "informacion.html", {
                'informacion': request.user,
                'error': error_message
            })

        request.user.set_password(new_password)
        request.user.save()
        # Mantener la sesión activa después del cambio de contraseña
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
        return redirect("informacion")

    return redirect("informacion")


@login_required
@role_required(["medico"])
def medico_consultas(request):
    consultas = Consulta.objects.filter(clave_medico=request.user)
    signos = SignosVitales.objects.filter(consulta__clave_medico=request.user)
    return render(request, "medico_consultas.html", {"consultas": consultas, "signos": signos})


@login_required
@role_required(["medico"])
def medico_historiales(request):
    query = request.GET.get('search', '')
    if query:
        historiales = HistorialMedico.objects.filter(id_historial__icontains=query)
    else:
        historiales = HistorialMedico.objects.all()
    return render(request, "medico_historiales.html", {"historiales": historiales, "query": query})

class HistorialMedicoForm(ModelForm):
    class Meta:
        model = HistorialMedico
        fields = ['enfermedades_cronicas', 'alergias', 'medicamento_usado', 'es_embarazada', 'usa_drogas', 'usa_cigarro', 'ingiere_alcohol']

@login_required
@role_required(["medico"])
def editar_historial(request, pk):
    historial = get_object_or_404(HistorialMedico, id_historial=pk)
    if request.method == 'POST':
        form = HistorialMedicoForm(request.POST, instance=historial)
        if form.is_valid():
            form.save()
            return redirect('medico_historiales')  # Cambia a la URL de tu vista principal
    else:
        form = HistorialMedicoForm(instance=historial)
    return render(request, 'editar_historial.html', {'form': form, 'historial': historial})