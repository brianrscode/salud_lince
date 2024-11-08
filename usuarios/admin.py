from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Medico, Paciente

class UsuarioAdmin(UserAdmin):
    model = Usuario

class MedicoAdmin(admin.ModelAdmin):
    # list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'fecha_nacimiento')
    list_display = ('matricula', 'nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'fecha_nacimiento')

class PacienteAdmin(admin.ModelAdmin):
    # list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'fecha_nacimiento')
    list_display = ('matricula', 'nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'fecha_nacimiento')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Medico, MedicoAdmin)
admin.site.register(Paciente, PacienteAdmin)
