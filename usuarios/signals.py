from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import HistorialMedico, Usuario
from consultas.models import Consulta

@receiver(post_migrate)
def crear_grupos_permisos(sender, **kwargs):
    # Definir permisos y grupos
    permisos_medico = [
        'view_consulta', 'add_consulta',
        'view_historialmedico',
        'view_usuario', 'change_usuario'
    ]
    permisos_paciente = [
        'view_consulta',
        'view_historialmedico', 'change_historialmedico',
        'view_usuario', 'change_usuario'
    ]

    # Crear grupos si no existen
    medico_group, _ = Group.objects.get_or_create(name="Medico")
    paciente_group, _ = Group.objects.get_or_create(name="Paciente")
    admin_group, _ = Group.objects.get_or_create(name="Administrador")

    # Obtener content types
    consulta_content_type = ContentType.objects.get_for_model(Consulta)
    historial_content_type = ContentType.objects.get_for_model(HistorialMedico)
    usuario_content_type = ContentType.objects.get_for_model(Usuario)

    # Asignar permisos al grupo Médico
    for permiso in permisos_medico:
        content_type = (
            consulta_content_type if 'consulta' in permiso
            else historial_content_type if 'historialmedico' in permiso
            else usuario_content_type
        )
        permission, _ = Permission.objects.get_or_create(
            codename=permiso, content_type=content_type
        )
        medico_group.permissions.add(permission)

    # Asignar permisos al grupo Paciente
    for permiso in permisos_paciente:
        content_type = (
            consulta_content_type if 'consulta' in permiso
            else historial_content_type if 'historialmedico' in permiso
            else usuario_content_type
        )
        permission, _ = Permission.objects.get_or_create(
            codename=permiso, content_type=content_type
        )
        paciente_group.permissions.add(permission)

    # Asignar todos los permisos al grupo Administrador
    all_permissions = Permission.objects.all()
    admin_group.permissions.set(all_permissions)

@receiver(post_save, sender=Usuario)
def asignar_grupo_y_crear_historial(sender, instance, created, **kwargs):
    if created:
        # Asignar grupo al usuario según su rol
        if instance.role == 'medico':
            medico_group = Group.objects.get(name='Medico')
            instance.groups.add(medico_group)
        elif instance.role == 'paciente':
            paciente_group = Group.objects.get(name='Paciente')
            instance.groups.add(paciente_group)
            # Crear el historial médico para el paciente
            HistorialMedico.objects.create(id_historial=instance.matricula, paciente=instance)
        elif instance.role == 'administrador':
            admin_group = Group.objects.get(name='Administrador')
            instance.groups.add(admin_group)
