from django.urls import path
from . import views

urlpatterns = [
    path('crear_consulta/', views.crear_consulta_view, name='crear_consulta'),
]
