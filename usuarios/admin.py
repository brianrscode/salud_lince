from django.contrib import admin
from .models import Usuario, HistorialMedico, Role


class UsuarioAdmin(admin.ModelAdmin):
    model = Usuario
    list_display = ('clave', 'nombres', 'role', 'is_staff')  # Lo que mostrará en la tabla
    ordering = ('email',)  # Cambiar 'username' por 'email' o el campo que prefieras ordenar
    list_filter = ('role', 'is_staff')  # Eliminar 'is_active' si no existe en tu modelo

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


class HistorialAdmin(admin.ModelAdmin):
    model = HistorialMedico
    list_display = ('id_historial', 'enfermedades_cronicas', 'alergias', 'medicamento_usado', 'es_embarazada', 'usa_drogas', 'usa_cigarro', 'ingiere_alcohol')
    ordering = ('id_historial',)
    list_filter = ('es_embarazada', 'usa_drogas', 'usa_cigarro', 'ingiere_alcohol')


class RoleAdmin(admin.ModelAdmin):
    model = Role
    list_display = ('nombre_rol', 'descripcion')
    ordering = ('nombre_rol',)
    list_filter = ('nombre_rol',)


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(HistorialMedico, HistorialAdmin)
admin.site.register(Role, RoleAdmin)