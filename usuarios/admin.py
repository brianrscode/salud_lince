from admin_extra_buttons.api import ExtraButtonsMixin, button
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
import pandas as pd

from .forms import BulkUserUploadForm
from .models import Area, HistorialMedico, Role, Usuario
from django.contrib.admin import AdminSite

class SitioAdminSoloSuperusuarios(AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

admin_site = SitioAdminSoloSuperusuarios(name='miadmin')


class UsuarioAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    model = Usuario
    list_display = ('clave', 'nombres', 'role', 'is_staff')
    ordering = ('email',)
    list_filter = ('role', 'is_staff')
    search_fields = ('clave', 'email', 'nombres',)

    def save_model(self, request, obj, form, change):
        # if not change:
        #     obj.set_password(form.cleaned_data['password'])

        # if not self.pk and not self.has_usable_password():
        #     self.set_password('P@ssword123')  # Cambia esto por la contraseña que desees
        if not change:
            # Si no se proporciona una contraseña, se asigna una por defecto
            password = form.cleaned_data.get('password')
            if not password:
                password = 'P@ssword123'  # Cambia esto por la contraseña que desees
            obj.set_password(password)

        super().save_model(request, obj, form, change)

    def get_urls(self):
        """Sobrescribe el método get_urls() para agregar la URL personalizada."""
        urls = super().get_urls()
        custom_urls = [
            path("bulk_upload", self.admin_site.admin_view(self.bulk_upload), name="bulk_upload"),
        ]
        return custom_urls + urls

    @button(label="Carga Masiva de Usuarios", html_attrs={"style": "background-color:#417690; color:white;"})
    def bulk_upload(self, request):
        if request.method == "POST":
            form = BulkUserUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["file"]
                try:
                    if file.name.endswith(".csv"):
                        df = pd.read_csv(file, dtype=str)  # Leer archivo como string
                    elif file.name.endswith(".xls") or file.name.endswith(".xlsx"):
                        df = pd.read_excel(file, dtype=str)  # Leer archivo como string
                    else:
                        messages.error(request, "Formato de archivo no compatible.")
                        return redirect("..")

                    usuarios_creados = 0
                    usuarios_actualizados = 0

                    for index, row in df.iterrows():
                        try:
                            # Validar valores vacíos y corregir tipos de datos
                            apellido_materno = str(row.get("apellido_materno", "")).strip() or None
                            valor_pas = row.get("password", "")
                            pas = "P@ssword123" if pd.isna(valor_pas) or str(valor_pas).strip() == "" else str(valor_pas).strip()

                            # Obtener el objeto del área
                            area_obj = Area.objects.get(carrera_o_puesto=row.get("carrera_o_puesto"))

                            # Asignar automáticamente el objeto Role según el área
                            area_nombre = area_obj.carrera_o_puesto.strip()
                            role_obj = None

                            if area_nombre == "Médico":
                                role_obj = Role.objects.get(nombre_rol="medico")
                            elif area_nombre == "ADMINISTRATIVO":
                                role_obj = Role.objects.get(nombre_rol="admin")
                            else:
                                role_obj = Role.objects.get(nombre_rol="paciente")


                            # print("Area y Role obtenidos:")
                            # print(area_obj.carrera_o_puesto)
                            # print(area_obj)
                            # print(role_obj)
                            # print(f"DEBUG: role_obj: {role_obj}, id: {getattr(role_obj, 'id', 'NO ID')}")
                            # print("-" * 20)


                            usuario, creado = Usuario.objects.update_or_create(
                                clave=row["clave"],
                                defaults={
                                    "email": row["email"],
                                    "nombres": row["nombres"],
                                    "apellido_paterno": row["apellido_paterno"],
                                    "apellido_materno": apellido_materno,
                                    "fecha_nacimiento": row.get("fecha_nacimiento", None),
                                    "sexo": row.get("sexo", None),
                                    "is_active": row.get("is_active", "True") == "True",
                                    "is_staff": row.get("is_staff", "False") == "True",
                                    "carrera_o_puesto_id": row.get("carrera_o_puesto", None),
                                    "role_id": role_obj.nombre_rol,
                                }
                            )

                            # Si es un usuario nuevo, se le asigna contraseña
                            if creado:
                                print("+" * 20)
                                print(f"Contraseña asignada: {pas}")
                                print("+" * 20)
                                usuario.set_password(pas)
                                usuarios_creados += 1
                            else:
                                usuarios_actualizados += 1

                            usuario.save()

                        except Exception as e:
                            messages.error(request, f"Error en la fila {index + 1}: {e}")

                    messages.success(request, f"Usuarios creados: {usuarios_creados}, actualizados: {usuarios_actualizados}.")
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
    search_fields = ('id_historial',)


class RoleAdmin(admin.ModelAdmin):
    model = Role
    list_display = ('nombre_rol', 'descripcion')
    ordering = ('nombre_rol',)
    list_filter = ('nombre_rol',)


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(HistorialMedico, HistorialAdmin)
admin.site.register(Role, RoleAdmin)
