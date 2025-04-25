from django.urls import path
from . import views

urlpatterns = [
    path('crear_consulta/', views.crear_consulta, name='crear_consulta'),
    path('api/recibir-frecuencia/', views.recibir_frecuencia, name='recibir_frecuencia'),
    path('api/obtener-ultima-frecuencia/', views.obtener_ultima_frecuencia, name='obtener_ultima_frecuencia'),

]
