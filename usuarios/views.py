import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django_ratelimit.decorators import ratelimit
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from consultas.models import CategoriaPadecimiento, Consulta, SignosVitales

from .decorators import role_required
from .forms import HistorialMedicoForm
from .forms import LoginForm
from .models import Area, HistorialMedico, Usuario


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role.nombre_rol == "medico":
            return redirect("medico_dashboard")  # Nombre de la vista para médicos
        elif request.user.role.nombre_rol == "paciente":
            return redirect("paciente_dashboard")  # Nombre de la vista para pacientes
        elif request.user.role.nombre_rol == "admin":
            return redirect("/admin/")  # Acceso para administradores

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
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
            else:
                messages.error(request, "Credenciales inválidas.")
        else:
            messages.error(request, "Formulario inválido.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    # if request.user.is_authenticated:
    logout(request)
    return redirect("login")


@login_required
@role_required(["medico"])
def medico_dashboard(request):
    ##################### Gráfica para hábitos de los pacientes #####################
    historiales = HistorialMedico.objects.filter(paciente__is_active=True)  # Todos los historiales médicos activos
    habitos = {  # Filtro de los hábitos de los pacientes
        'Fuman': historiales.filter(usa_cigarro=True).count(),  # Cantidad de pacientes que fuman
        'Ingiere Alcohol': historiales.filter(ingiere_alcohol=True).count(),  # Cantidad de pacientes que ingieren alcohol
        'Usa Drogas': historiales.filter(usa_drogas=True).count(),  # Cantidad de pacientes que usan drogas
        'Embarazadas': historiales.filter(es_embarazada=True).count(),  # Cantidad de pacientes embarazadas
        'Usa Lentes': historiales.filter(usa_lentes=True).count(),  # Cantidad de pacientes que usan lentes
        'vida sexual activa': historiales.filter(vida_sexual_activa=True).count(),  # Cantidad de pacientes que tienen vida sexual activa
        'Usa Métodos anticonceptivos': historiales.filter(usa_metodos_anticonceptivos=True).count(),  # Cantidad de pacientes que usan metodos anticonceptivos
    }
    habitos_fig = go.Figure([go.Bar(x=list(habitos.keys()), y=list(habitos.values()), marker_color='indianred')])
    habitos_fig.update_layout(title_text="Pacientes con Hábitos", xaxis_title="Hábito", yaxis_title="Cantidad")

    #####################Gráfica para tipos de consultas #####################
    consultas = Consulta.objects.values('categoria_de_padecimiento').annotate(total=Count('categoria_de_padecimiento'))
    padecimientos_dict = {p.id_padecimiento: p.padecimiento for p in CategoriaPadecimiento.objects.all()}

    consultas_fig = px.bar(
        x=[padecimientos_dict.get(c['categoria_de_padecimiento'], "OTROS") for c in consultas],  # Nombres de tipos de consulta
        y=[c['total'] for c in consultas],  # Cantidad de pacientes por tipo de consulta
        title="Distribución de Tipos de Consultas"
    )

    ##################### Gráfica de barras de cantidad de pacientes por area #####################
    carrera_o_puesto = Usuario.objects.values('carrera_o_puesto_id').annotate(total=Count('carrera_o_puesto_id'))
    areas_fig = go.Figure([go.Bar(x=[c['carrera_o_puesto_id'] for c in carrera_o_puesto], y=[c['total'] for c in carrera_o_puesto], marker_color='indianred')])
    areas_fig.update_layout(title_text="Distribución de Areas", xaxis_title="Area", yaxis_title="Cantidad")

    ##################### Gráfica de barras de cantidad de pacientes categoría de padecimiento #####################
    datos = Consulta.objects.values("clave_paciente__carrera_o_puesto_id", "categoria_de_padecimiento").annotate(total=Count("clave_paciente__carrera_o_puesto_id"))
    df = pd.DataFrame(datos)
    df["categoria_de_padecimiento"] = df["categoria_de_padecimiento"].map(padecimientos_dict)
    labels = {
        "categoria_de_padecimiento": "Categoría de Padecimiento",  # Personaliza el label del eje x
        "total": "Total de Pacientes",  # Personaliza el label del eje y
        "clave_paciente__carrera_o_puesto_id": "Área o Puesto"  # Personaliza el label de la leyenda
    }
    padecimientos_fig = px.bar(
        df,
        x="categoria_de_padecimiento",
        y="total",
        color="clave_paciente__carrera_o_puesto_id",
        barmode="group",
        title="Distribución de Pacientes por Área y Tipo de Consulta",
        labels=labels
    )


    return render(request, 'medico_dashboard.html', {
        'habitos_graph': habitos_fig.to_html(full_html=False),  # Gráfica de barras
        'consultas_graph': consultas_fig.to_html(full_html=False),  # Gráfica de pastel
        'areas_graph': areas_fig.to_html(full_html=False),
        'padecimientos_graph': padecimientos_fig.to_html(full_html=False),
    })

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
    consultas = Consulta.objects.filter(clave_paciente=request.user).select_related('signos_vitales')

    paginador = Paginator(consultas, 20)  # Mostrar 10 consultas por páginas
    pagina = request.GET.get('page', 1)
    try:
        consultas = paginador.page(pagina)
    except PageNotAnInteger:
        consultas = paginador.page(1)
    except EmptyPage:
        consultas = paginador.page(paginador.num_pages)

    return render(request, "paciente_consultas.html", {"consultas": consultas})



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
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,15}$', new_password):
            messages.error(request, "La contraseña debe tener al entre 8 y 15 caracteres, incluir una letra mayúscula, un número y un caracter especial.")
            return redirect("informacion")
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,15}$', confirm_password):
            messages.error(request, "La contraseña debe tener al entre 8 y 15 caracteres, incluir una letra mayúscula, un número y un caracter especial.")
            return redirect("informacion")

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
    mostrar_todas = request.GET.get('todas', '0') == '1'  # Leer parámetro 'todas'
    if mostrar_todas:
        # Mostrar primero la consulta con el més reciente
        consultas = Consulta.objects.select_related('clave_medico', 'clave_paciente', 'signos_vitales').all()
    else:
        consultas = Consulta.objects.select_related('clave_medico', 'clave_paciente', 'signos_vitales').filter(clave_medico=request.user)

    paginador = Paginator(consultas, 20)  # Mostrar 10 consultas por páginas
    pagina = request.GET.get('page', 1)
    try:
        consultas = paginador.page(pagina)
    except PageNotAnInteger:
        consultas = paginador.page(1)
    except EmptyPage:
        consultas = paginador.page(paginador.num_pages)

    return render(request, "medico_consultas.html", {
        "consultas": consultas,
        "mostrar_todas": mostrar_todas
    })


@login_required
@role_required(["medico"])
def medico_historiales(request):
    query = request.GET.get('search', '')
    # Si hay una consulta, filtrar los historiales de acuerdo a la consulta
    if query:
        historiales = HistorialMedico.objects.filter(
            id_historial__icontains=query,
            paciente__role__nombre_rol='paciente',
            paciente__is_active=True
        ).exclude(paciente__carrera_o_puesto__carrera_o_puesto="Médico").order_by('id_historial')
    else:
        historiales = HistorialMedico.objects.filter(
            paciente__role__nombre_rol='paciente',
            paciente__is_active=True
        ).exclude(paciente__carrera_o_puesto__carrera_o_puesto="Médico").order_by('id_historial')

    paginador = Paginator(historiales, 10)  # Mostrar 10 consultas por páginas
    pagina = request.GET.get('page', 1)
    try:
        historiales = paginador.page(pagina)
    except PageNotAnInteger:
        historiales = paginador.page(1)
    except EmptyPage:
        historiales = paginador.page(paginador.num_pages)

    return render(request, "medico_historiales.html", {"historiales": historiales, "query": query})


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
