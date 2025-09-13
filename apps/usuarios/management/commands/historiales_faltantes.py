from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import HistorialMedico, Role

class Command(BaseCommand):
    help = 'Crea historiales médicos para los pacientes que no los tengan'

    def handle(self, *args, **options):
        # Obtener el modelo de usuario personalizado
        Usuario = get_user_model()

        # Obtener el rol de paciente
        try:
            rol_paciente = Role.objects.get(nombre_rol='paciente')
        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR('No existe el rol "paciente" en la base de datos'))
            return

        # Obtener pacientes sin historial médico
        # Usamos 'historial' que es el related_name definido en el modelo
        pacientes_sin_historial = Usuario.objects.filter(
            role=rol_paciente,
            historial__isnull=True  # Cambiado a 'historial' en lugar de 'historialmedico'
        )

        total = pacientes_sin_historial.count()
        self.stdout.write(f'Encontrados {total} pacientes sin historial médico')

        # Crear historiales faltantes
        creados = 0
        for paciente in pacientes_sin_historial:
            # Verificar que el paciente no sea médico
            if (hasattr(paciente, 'carrera_o_puesto') and
                paciente.carrera_o_puesto != 'Médico'):

                HistorialMedico.objects.get_or_create(
                    id_historial=paciente.clave,
                    defaults={'paciente': paciente}
                )
                creados += 1
                if creados % 100 == 0:  # Mostrar progreso cada 100 registros
                    self.stdout.write(f'Procesados {creados} de {total}...')

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {creados} historiales médicos nuevos')
        )