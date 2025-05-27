from django.urls import path
from . import views

urlpatterns = [
    path('crear_consulta/', views.crear_consulta_view, name='crear_consulta'),
    path('api/recibir-frecuencia/', views.recibir_frecuencia_view, name='recibir_frecuencia'),
    path('api/obtener-ultima-frecuencia/', views.obtener_ultima_frecuencia_view, name='obtener_ultima_frecuencia'),
    path('api/buscar-paciente/', views.buscar_paciente_por_clave_view, name='buscar_paciente'),

]
