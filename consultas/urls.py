from django.urls import path
from . import views

urlpatterns = [
    path('crear_consulta/', views.crear_consulta, name='crear_consulta'),
]
