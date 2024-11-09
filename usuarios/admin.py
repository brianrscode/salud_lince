from django.contrib import admin
from django import forms
from .models import Usuario, Medico, HistorialMedico, Paciente


class MedicoAdmin(admin.ModelAdmin):
    list_display = ('usuario',)  # Muestra el usuario asociado en la lista de médicos

admin.site.register(Medico, MedicoAdmin)

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nombres', 'email', 'is_staff')  # Muestra los campos relevantes en la lista de usuarios
    search_fields = ('matricula', 'email')

admin.site.register(Usuario, UsuarioAdmin)

class PacienteAdmin(admin.ModelAdmin):
    list_display = ('usuario',)  # Muestra los campos relevantes en la lista de pacientes
    search_fields = ('matricula', )

admin.site.register(Paciente, PacienteAdmin)

class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = ('paciente', )  # Muestra los campos relevantes en la lista de historiales médicos
    search_fields = ('matricula', )

admin.site.register(HistorialMedico, HistorialMedicoAdmin)