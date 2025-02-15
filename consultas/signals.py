from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import Consulta, SignosVitales, MotivoConsulta


# @receiver(post_save, sender=Consulta)
# def crear_signos_vitales(sender, instance, created, **kwargs):
#     '''Crea un SignosVitales cuando se crea una Consulta'''
#     if created:
#         SignosVitales.objects.create(consulta=instance)


@receiver(post_migrate)
def crear_motivos_de_consultas(sender, **kwargs):
    motivos = [
        "IRAS",
        "GASTROINTESTINALES",
        "CONTROL PARENTAL",
        "CEFALEA",
        "QUEMADURAS",
        "LESIONES/HERIDAS",
        "MORDEDURA DE ",
        "OTROS",
        "HIPERTENSIÓN",
        "DIABETES",
        "OBESIDAD",
        "ALERGIAS",
        "CARDIOVASCULARES",
        "ANSIEDAD",
        "GINECOLÓGICO",
        "SINCOPE",
        "ASESORÍA",
    ]

    for motivoC in motivos:
        MotivoConsulta.objects.get_or_create(motivo=motivoC)