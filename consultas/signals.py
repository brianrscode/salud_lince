from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import Consulta, SignosVitales, CategoriaPadecimiento


# @receiver(post_save, sender=Consulta)
# def crear_signos_vitales(sender, instance, created, **kwargs):
#     '''Crea un SignosVitales cuando se crea una Consulta'''
#     if created:
#         SignosVitales.objects.create(consulta=instance)


@receiver(post_migrate)
def crear_motivos_de_consultas(sender, **kwargs):
    padecimientos = [
        "IRAS",
        "GASTROINTESTINALES",
        "CONTROL PARENTAL",
        "CEFALEA",
        "QUEMADURAS",
        "LESIONES/HERIDAS",
        "MORDEDURA DE PERRO",
        "OTROS",
        "HIPERTENSIÓN",
        "DIABETES MELLITUS",
        "OBESIDAD",
        "ALERGIAS",
        "CARDIOVASCULARES",
        "NEUROLÓGICOS",
        "ANSIEDAD",
        "GINECOLÓGICO",
        "OFTALMICO",
        "MUSCULOESQUELETICO",
        "SINCOPE",
        "ASESORÍA",
    ]

    for padecimientoC in padecimientos:
        CategoriaPadecimiento.objects.get_or_create(padecimiento=padecimientoC)