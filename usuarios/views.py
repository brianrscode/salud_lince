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
        rol = request.user.role.nombre_rol
        if rol == "medico":
            return redirect("medico_dashboard")
        if rol == "paciente":
            return redirect("paciente_dashboard")
        if rol == "admin":
            return redirect("/admin/")

        messages.error(request, "Rol no reconocido.")
        return redirect("login")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Formulario inválido.")
            return render(request, "login.html", {"form": form})

        clave = form.cleaned_data["clave"]
        password = form.cleaned_data["password"]
        user = authenticate(request, clave=clave, password=password)

        if user is None:
            messages.error(request, "Credenciales inválidas.")
            return render(request, "login.html", {"form": form})

        login(request, user)
        rol = user.role.nombre_rol
        if rol == "medico":
            return redirect("medico_dashboard")
        if rol == "paciente":
            return redirect("paciente_dashboard")
        if rol == "admin":
            return redirect("/admin/")

        messages.error(request, "Rol no reconocido.")
        return redirect("login")

    form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    """
    vista desloguiar al usuario 

    Returns: 
        HttpResponse: respuesta http dirigida a la vista de inicio de sesión
    """
    logout(request)
    return redirect("login")


@login_required
@role_required(["medico"])
def medico_dashboard(request):
    ##################### Gráfica para hábitos de los pacientes #####################
    historiales = HistorialMedico.objects.filter(paciente__is_active=True)
    habitos = {
        'Fuman': historiales.filter(usa_cigarro=True).count(),
        'Ingiere Alcohol': historiales.filter(ingiere_alcohol=True).count(),
        'Usa Drogas': historiales.filter(usa_drogas=True).count(),
        'Embarazadas': historiales.filter(es_embarazada=True).count(),
        'Usa Lentes': historiales.filter(usa_lentes=True).count(),
        'vida sexual activa': historiales.filter(vida_sexual_activa=True).count(),
        'Usa Métodos anticonceptivos': historiales.filter(usa_metodos_anticonceptivos=True).count(),
    }
    habitos_fig = go.Figure([go.Bar(x=list(habitos.keys()), y=list(habitos.values()), marker_color='indianred')])
    habitos_fig.update_layout(title_text="Pacientes con Hábitos", xaxis_title="Hábito", yaxis_title="Cantidad")

    ##################### Gráfica para tipos de consultas #####################
    consultas = Consulta.objects.values('categoria_de_padecimiento').annotate(total=Count('categoria_de_padecimiento'))
    padecimientos_dict = {p.id_padecimiento: p.padecimiento for p in CategoriaPadecimiento.objects.all()}

    if consultas:
        consultas_fig = px.bar(
            x=[padecimientos_dict.get(c['categoria_de_padecimiento'], "OTROS") for c in consultas],
            y=[c['total'] for c in consultas],
            title="Distribución de Tipos de Consultas"
        )
    else:
        consultas_fig = go.Figure()
        consultas_fig.update_layout(
            title="Distribución de Tipos de Consultas",
            annotations=[{
                'text': "No hay datos de consultas",
                'xref': "paper", 'yref': "paper",
                'showarrow': False, 'font': {'size': 18}
            }]
        )

    ##################### Gráfica de barras de cantidad de pacientes por área #####################
    carrera_o_puesto = Usuario.objects.values('carrera_o_puesto_id').annotate(total=Count('carrera_o_puesto_id'))
    areas_fig = go.Figure([go.Bar(
        x=[c['carrera_o_puesto_id'] for c in carrera_o_puesto],
        y=[c['total'] for c in carrera_o_puesto],
        marker_color='indianred'
    )])
    areas_fig.update_layout(title_text="Distribución de Áreas", xaxis_title="Área", yaxis_title="Cantidad")

    ##################### Gráfica por área y tipo de consulta #####################
    datos = Consulta.objects.values("clave_paciente__carrera_o_puesto_id", "categoria_de_padecimiento").annotate(total=Count("clave_paciente__carrera_o_puesto_id"))
    if datos:
        df = pd.DataFrame(datos)
        df["categoria_de_padecimiento"] = df["categoria_de_padecimiento"].map(padecimientos_dict)
        labels = {
            "categoria_de_padecimiento": "Categoría de Padecimiento",
            "total": "Total de Pacientes",
            "clave_paciente__carrera_o_puesto_id": "Área o Puesto"
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
    else:
        padecimientos_fig = go.Figure()
        padecimientos_fig.update_layout(
            title="Distribución de Pacientes por Área y Tipo de Consulta",
            annotations=[{
                'text': "No hay datos suficientes",
                'xref': "paper", 'yref': "paper",
                'showarrow': False, 'font': {'size': 18}
            }]
        )

    ##################### Gráfica de género #####################
    pacientes_por_consultas = Consulta.objects.values('clave_paciente__clave', 'clave_paciente__sexo', 'clave_paciente__carrera_o_puesto_id')
    df_genero_por_carrera = pd.DataFrame(pacientes_por_consultas)
    df_genero_por_carrera = df_genero_por_carrera.drop_duplicates(subset=['clave_paciente__clave'])

    if not df_genero_por_carrera.empty:
        cantidad_hombres = df_genero_por_carrera[df_genero_por_carrera['clave_paciente__sexo'] == 'M'].count()['clave_paciente__clave']
        cantidad_mujeres = df_genero_por_carrera[df_genero_por_carrera['clave_paciente__sexo'] == 'F'].count()['clave_paciente__clave']
        df_genero_por_carrera = df_genero_por_carrera.groupby(['clave_paciente__carrera_o_puesto_id', 'clave_paciente__sexo']).size().reset_index(name='cantidad')

        genero_fig = px.bar(
            df_genero_por_carrera,
            x="clave_paciente__carrera_o_puesto_id",
            y="cantidad",
            color="clave_paciente__sexo",
            barmode="group",
            title="Cantidad de Pacientes por Carrera/Puesto y Género",
            labels={"clave_paciente__carrera_o_puesto_id": "Carrera/Puesto", "cantidad": "Cantidad de Pacientes", "clave_paciente__sexo": "Género"}
        )

        genero_pastel = go.Figure(data=[go.Pie(labels=['Hombres', 'Mujeres'], values=[cantidad_hombres, cantidad_mujeres])])
        genero_pastel.update_layout(title_text="Distribución de Pacientes por Género", title_x=0.5)
    else:
        genero_fig = go.Figure()
        genero_fig.update_layout(
            title="Cantidad de Pacientes por Carrera/Puesto y Género",
            annotations=[{
                'text': "No hay datos de género",
                'xref': "paper", 'yref': "paper",
                'showarrow': False, 'font': {'size': 18}
            }]
        )

        genero_pastel = go.Figure()
        genero_pastel.update_layout(
            title="Distribución de Pacientes por Género",
            annotations=[{
                'text': "No hay datos disponibles",
                'xref': "paper", 'yref': "paper",
                'showarrow': False, 'font': {'size': 18}
            }]
        )

    return render(request, 'medico_dashboard.html', {
        'genero_pastel': genero_pastel.to_html(full_html=False),
        'genero_graph': genero_fig.to_html(full_html=False),
        'habitos_graph': habitos_fig.to_html(full_html=False),
        'consultas_graph': consultas_fig.to_html(full_html=False),
        'areas_graph': areas_fig.to_html(full_html=False),
        'padecimientos_graph': padecimientos_fig.to_html(full_html=False),
    })


@login_required
@role_required(["paciente"])
def paciente_dashboard(request):
    return render(request, "paciente_dashboard.html")


@ratelimit(key='ip', rate='5/m', method='GET', block=True)
@login_required
@role_required(["paciente"])
def historial_view(request):
    # obtener el historial médico del paciente
    historial = request.user.historial
    return render(request, "historial_medico.html", {"historial": historial})


@ratelimit(key='ip', rate='10/m', method='GET', block=True)
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


@ratelimit(key='ip', rate='5/m', method='GET', block=True)
@login_required
@role_required(["paciente", "medico"])
def usuario_informacion(request):
    informacion = request.user
    return render(request, "informacion.html", {"informacion": informacion})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='ip', rate='10/m', method='GET', block=True)
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

@ratelimit(key='ip', rate='10/m', method='GET', block=True)
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
