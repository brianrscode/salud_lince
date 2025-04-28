import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django_ratelimit.decorators import ratelimit
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from consultas.models import CategoriaPadecimiento, Consulta, SignosVitales

from .decorators import role_required
from .forms import HistorialMedicoForm
from .forms import LoginForm
from .models import Area, HistorialMedico, Usuario


@never_cache
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def login_view(request):
    """
    Vista para iniciar sesión de usuarios según su rol.

    Si el usuario ya está autenticado, lo redirige a su panel correspondiente.
    Si no, procesa el formulario de inicio de sesión (LoginForm).

    Returns:
        HttpResponse: Redirección al panel de usuario correspondiente o renderizado del formulario de login.
    """
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


@never_cache
def logout_view(request):
    """
    vista desloguear al usuario

    Returns:
        HttpResponse: respuesta http dirigida a la vista de inicio de sesión
    """
    logout(request)
    return redirect("login")


@never_cache
@login_required
@role_required(["medico"])
def medico_dashboard(request):
    """
    Vista del panel principal para los médicos.

    Genera dos gráficas:
    1. Distribución de hábitos en los pacientes activos.
    2. Distribución de tipos de consultas realizadas.

    Requiere:
        - Que el usuario esté autenticado.
        - Que el usuario tenga el rol de 'medico'.

    Returns:
        HttpResponse: Renderizado de la plantilla con las gráficas.
    """
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
    # Obtenemos la cantidad de usuarios agrupados por su carrera o puesto
    carrera_o_puesto = Usuario.objects.values('carrera_o_puesto_id').annotate(total=Count('carrera_o_puesto_id'))
    # Creamos la gráfica de barras con Plotly para mostrar cuántos pacientes hay por área
    areas_fig = go.Figure([go.Bar(
        x=[c['carrera_o_puesto_id'] for c in carrera_o_puesto],
        y=[c['total'] for c in carrera_o_puesto],
        marker_color='indianred'
    )])
    # Configuramos los títulos de la gráfica
    areas_fig.update_layout(title_text="Distribución de Áreas", xaxis_title="Área", yaxis_title="Cantidad")

    ##################### Gráfica por área y tipo de consulta #####################
    # Obtenemos la cantidad de consultas agrupadas por área (carrera/puesto) y tipo de padecimiento
    datos = Consulta.objects.values("clave_paciente__carrera_o_puesto_id", "categoria_de_padecimiento").annotate(total=Count("clave_paciente__carrera_o_puesto_id"))
    # Verificamos si existen datos para construir la gráfica
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
    # Obtener los datos de los pacientes que han tenido consultas, incluyendo clave, sexo y carrera/puesto
    pacientes_por_consultas = Consulta.objects.values('clave_paciente__clave', 'clave_paciente__sexo', 'clave_paciente__carrera_o_puesto_id')
    # Convertimos los datos a un DataFrame de pandas para facilitar el análisis
    df_genero_por_carrera = pd.DataFrame(pacientes_por_consultas)
    # Eliminamos duplicados para contar solo una vez a cada paciente
    df_genero_por_carrera = df_genero_por_carrera.drop_duplicates(subset=['clave_paciente__clave'])

    # Verificamos si hay datos disponibles antes de generar las gráficas
    if not df_genero_por_carrera.empty:
        cantidad_hombres = df_genero_por_carrera[df_genero_por_carrera['clave_paciente__sexo'] == 'M'].count()['clave_paciente__clave']
        cantidad_mujeres = df_genero_por_carrera[df_genero_por_carrera['clave_paciente__sexo'] == 'F'].count()['clave_paciente__clave']
        df_genero_por_carrera = df_genero_por_carrera.groupby(['clave_paciente__carrera_o_puesto_id', 'clave_paciente__sexo']).size().reset_index(name='cantidad')

        # Creamos la gráfica de barras para mostrar la distribución por carrera/puesto y género
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
        # Si no hay datos, se muestran gráficas vacías con un mensaje correspondiente
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


@never_cache
@login_required
@role_required(["paciente"])
def paciente_dashboard(request):
    """
    Vista del panel principal para los pacientes.

    Requiere:
        - Que el usuario esté autenticado.
        - Que el usuario tenga el rol de 'paciente'.

    Returns:
        HttpResponse: Renderizado de la plantilla del dashboard del paciente.
    """
    return render(request, "paciente_dashboard.html")


@never_cache
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
@login_required
@role_required(["paciente"])
def historial_view(request):
    """
    Vista para mostrar el historial médico del paciente.

    Requiere:
        - Autenticación del usuario.
        - Que el usuario tenga el rol de 'paciente'.
        - No más de 5 solicitudes GET por minuto por IP.

    Returns:
        HttpResponse: Renderizado de la plantilla con el historial médico del paciente.
    """
    # obtener el historial médico del paciente
    historial = request.user.historial
    return render(request, "historial_medico.html", {"historial": historial})


@never_cache
@ratelimit(key='ip', rate='10/m', method='GET', block=True)
@login_required
@role_required(["paciente"])
def paciente_consultas(request):
    """
    Vista para mostrar las consultas médicas del paciente autenticado.

    Aplica paginación para mostrar un número limitado de consultas por página.
    """
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


@never_cache
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
@login_required
@role_required(["paciente", "medico"])
def usuario_informacion(request):
    """
    Vista para mostrar la información básica del usuario autenticado.

    Esta vista es accesible tanto para pacientes como médicos.
    """
    informacion = request.user
    return render(request, "informacion.html", {"informacion": informacion})


@never_cache
@ratelimit(key='ip', rate='5/m', method='POST', block=True) # Limite 5 solicitudes POST por minuto por IP
@ratelimit(key='ip', rate='10/m', method='GET', block=True) # Limite 10 solicitudes GET por minuto por IP
@login_required
@role_required(["paciente", "medico"])
def cambiar_contrasena(request):
    """
    Vista que permite al usuario cambiar su contraseña.

    Solo es accesible para usuarios autenticados con los roles 'paciente' o 'medico'.
    La contraseña debe cumplir con ciertos requisitos de seguridad.
    """
    if request.method == 'POST': # Solo se ejecuta si la solicitud es de tipo POST
        # Obtención de las contraseñas ingresadas por el usuario desde el formulario
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        # Validación de la nueva contraseña con expresión regular (mínimo 8 y máximo 15 caracteres,
        # debe incluir al menos una letra mayúscula, un número y un carácter especial)
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,15}$', new_password):
            messages.error(request, "La contraseña debe tener al entre 8 y 15 caracteres, incluir una letra mayúscula, un número y un caracter especial.")
            return redirect("informacion") # Redirige si no cumple con los requisitos

         # Validación para la confirmación de la nueva contraseña
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,15}$', confirm_password):
            messages.error(request, "La contraseña debe tener al entre 8 y 15 caracteres, incluir una letra mayúscula, un número y un caracter especial.")
            return redirect("informacion") # Redirige si no cumple con los requisitos

        # Verificación de que la contraseña actual ingresada por el usuario sea correcta
        if not request.user.check_password(current_password):
            error_message = 'La contraseña actual es incorrecta.'
            return render(request, "informacion.html", {
                'informacion': request.user,
                'error': error_message
            })

        # Verificación de que la nueva contraseña y la confirmación coincidan
        if new_password != confirm_password:
            error_message = 'Las contraseñas no coinciden.'
            return render(request, "informacion.html", {
                'informacion': request.user,
                'error': error_message
            })

        # Si todo es correcto, se cambia la contraseña del usuario
        request.user.set_password(new_password)
        request.user.save()
        # Mantener la sesión activa después del cambio de contraseña
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
        return redirect("informacion")

    return redirect("informacion")


@never_cache
@ratelimit(key='ip', rate='10/m', method='GET', block=True) # Limite 10 solicitudes GET por minuto por IP
@login_required
@role_required(["medico"])
def medico_consultas(request):
    """
    Vista para que los médicos vean sus consultas o todas las consultas si así lo desean.

    Si el parámetro 'todas' está presente en la URL, se mostrarán todas las consultas.
    Si no, se mostrarán solo las consultas relacionadas con el médico autenticado.
    """
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


@never_cache
@login_required
@role_required(["medico"])
def medico_historiales(request):
    """
    Vista para que los médicos vean los historiales médicos de los pacientes.

    Si se proporciona un parámetro de búsqueda, los historiales se filtrarán de acuerdo al ID del historial.
    También se paginan los resultados para mostrar solo una cantidad limitada por página.
    """
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



@never_cache
@login_required
@role_required(["medico"])
def editar_historial(request, pk):
    """
    Vista que permite al médico editar un historial médico existente.

    Solo se permite a los médicos editar los historiales de los pacientes.
    Si la solicitud es de tipo POST, se guarda el formulario con los nuevos datos,
    de lo contrario, se muestra el formulario con los datos actuales del historial.
    """
    historial = get_object_or_404(HistorialMedico, id_historial=pk)
    datos = request.POST if request.method == 'POST' else None
    form = HistorialMedicoForm(datos, instance=historial)

    if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect('medico_historiales')

    return render(request, 'editar_historial.html', {'form': form, 'historial': historial})
