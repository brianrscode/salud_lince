from django.contrib import admin
from .models import Usuario, HistorialMedico, Role


class UsuarioAdmin(admin.ModelAdmin):
    model = Usuario
    list_display = ('email', 'nombres', 'role', 'is_staff')
    ordering = ('email',)  # Cambiar 'username' por 'email' o el campo que prefieras ordenar
    list_filter = ('role', 'is_staff')  # Eliminar 'is_active' si no existe en tu modelo

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(HistorialMedico)
admin.site.register(Role)