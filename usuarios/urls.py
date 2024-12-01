from django.urls import path
from . import views

urlpatterns = [
    # Login
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("medico/dashboard/", views.medico_dashboard, name="medico_dashboard"),
    path("paciente/dashboard/", views.paciente_dashboard, name="paciente_dashboard"),
    path("paciente/historial/", views.historial_view, name="historial"),
    path("paciente/mis_consultas/", views.paciente_consultas, name="paciente_consultas"),
    path("paciente/informacion/", views.paciente_informacion, name="paciente_informacion"),
    path("cambiar_contrasena/", views.cambiar_contrasena, name="cambiar_contrasena"),

    path("medico/informacion/", views.medico_informacion, name="medico_informacion"),
    path("medico/consultas/", views.medico_consultas, name="medico_consultas"),
    path("medico/historiales/", views.medico_historiales, name="medico_historiales"),
]