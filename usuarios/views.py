from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from consultas.models import Consulta, SignosVitales
from django.contrib import admin
from django.http import HttpResponse


def login_view(request):
    if request.method == "POST":
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