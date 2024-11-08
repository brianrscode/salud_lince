from django.contrib import admin
from .models import Usuario


# Gestionar usuarios desde el panel de administración
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # Campos a mostrar en el panel de administración
    list_display = ('username', 'tipo_usuario', 'telefono', 'direccion')
    # Campos de búsqueda
    search_fields = ('username', 'tipo_usuario')