import pandas as pd
from django.contrib import admin, messages
from .models import Usuario, HistorialMedico, Role
from django.shortcuts import render, redirect
from django.urls import path, reverse
from .forms import BulkUserUploadForm

# class UsuarioAdmin(admin.ModelAdmin):
#     model = Usuario
#     list_display = ('clave', 'nombres', 'role', 'is_staff')  # Lo que mostrará en la tabla
#     ordering = ('email',)  # Cambiar 'username' por 'email' o el campo que prefieras ordenar
#     list_filter = ('role', 'is_staff')  # Eliminar 'is_active' si no existe en tu modelo

#     def save_model(self, request, obj, form, change):
#         if not change:
#             obj.set_password(form.cleaned_data['password'])
#         super().save_model(request, obj, form, change)
class UsuarioAdmin(admin.ModelAdmin):
    model = Usuario
    list_display = ('clave', 'nombres', 'role', 'is_staff')
    ordering = ('email',)
    list_filter = ('role', 'is_staff')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    # 📌 Agregar botón en la parte superior de la lista de usuarios
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["bulk_upload_url"] = reverse("admin:bulk_upload")
        return super().changelist_view(request, extra_context=extra_context)

    # 📌 Agregar URL personalizada para carga masiva
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("bulk_upload/", self.admin_site.admin_view(self.bulk_upload), name="bulk_upload"),
        ]
        return custom_urls + urls

    # 📌 Lógica de carga masiva de usuarios
    def bulk_upload(self, request):
        if request.method == "POST":
            form = BulkUserUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["file"]
                try:
                    if file.name.endswith(".csv"):
                        df = pd.read_csv(file, dtype=str)
                    elif file.name.endswith(".xls") or file.name.endswith(".xlsx"):
                        df = pd.read_excel(file, dtype=str)
                    else:
                        messages.error(request, "Formato de archivo no compatible.")
                        return redirect("..")

                    usuarios_creados = 0
                    usuarios_omitidos = 0
                    errores = []

                    for index, row in df.iterrows():
                        try:
                            usuario, creado = Usuario.objects.get_or_create(
                                clave=row["clave"],
                                defaults={
                                    "email": row["email"],
                                    "nombres": row["nombres"],
                                    "apellido_paterno": row["apellido_paterno"],
                                    "apellido_materno": row.get("apellido_materno", ""),
                                    "fecha_nacimiento": row.get("fecha_nacimiento", None),
                                    "sexo": row.get("sexo", None),
                                    "usuario_activo": row.get("usuario_activo", "True") == "True",
                                    "is_staff": row.get("is_staff", "False") == "True",
                                    "carrera_o_puesto_id": row.get("carrera_o_puesto", None),
                                    "role_id": row.get("role", None),
                                }
                            )

                            # Si el usuario ya existía, lo omitimos
                            if not creado:
                                usuarios_omitidos += 1
                                continue

                            # Solo establecer la contraseña para usuarios nuevos
                            usuario.set_password(row.get("password", "Default@123"))
                            usuario.save()
                            usuarios_creados += 1

                        except Exception as e:
                            errores.append(f"Error en la fila {index + 1}: {e}")

                    if errores:
                        messages.warning(request, f"Usuarios creados: {usuarios_creados}, omitidos: {usuarios_omitidos}. Errores en {len(errores)} filas.")
                        for error in errores[:5]:  # Mostrar solo los primeros 5 errores
                            messages.error(request, error)
                    else:
                        messages.success(request, f"Se han creado {usuarios_creados} usuarios. {usuarios_omitidos} ya existían y fueron ignorados.")

                    return redirect("..")

                except Exception as e:
                    messages.error(request, f"Ocurrió un error: {e}")
                    return redirect("..")
        else:
            form = BulkUserUploadForm()

        return render(request, "admin_custom/bulk_upload.html", {"form": form, "opts": self.model._meta})



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