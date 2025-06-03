from django.urls import path
from . import views

urlpatterns = [
    path('crear_consulta/', views.crear_consulta_view, name='crear_consulta'),
    path('api/buscar-paciente/', views.buscar_paciente_por_clave_view, name='buscar_paciente'),
]
