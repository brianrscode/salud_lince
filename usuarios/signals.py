# usuarios/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, HistorialMedico

@receiver(post_save, sender=Usuario)
def crear_historial_medico(sender, instance, created, **kwargs):
    # Solo crea el historial si el usuario es un "paciente" y se ha creado un nuevo registro
    if created and instance.role == 'paciente':
        # Crear historial médico
        HistorialMedico.objects.create(id_historial=instance.matricula, paciente=instance)
