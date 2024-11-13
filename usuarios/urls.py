from django.urls import path
from . import views

urlpatterns = [
    # Login
    path('login/', views.login, name='login'),
    path('medicos/', views.medicos, name='medicos'),
    path('pacientes/', views.pacientes, name='pacientes'),
]