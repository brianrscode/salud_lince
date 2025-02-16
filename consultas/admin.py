from django.contrib import admin
from .models import Consulta, SignosVitales


class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('id_consulta', 'fecha', 'padecimiento_actual', 'categoria_de_padecimiento', 'clave_paciente', 'clave_medico')
    ordering = ('id_consulta',)
    list_filter = ('fecha', 'categoria_de_padecimiento', 'clave_paciente', 'clave_medico')


class SignosVitalesAdmin(admin.ModelAdmin):
    list_display = ('id_signos', 'peso', 'talla', 'temperatura', 'frecuencia_cardiaca', 'frecuencia_respiratoria', 'presion_arterial')
    ordering = ('id_signos',)


admin.site.register(Consulta, ConsultaAdmin)
admin.site.register(SignosVitales, SignosVitalesAdmin)