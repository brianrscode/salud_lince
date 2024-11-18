from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consulta, SignosVitales

@receiver(post_save, sender=Consulta)
def crear_signos_vitales(sender, instance, created, **kwargs):
    '''Crea un SignosVitales cuando se crea una Consulta'''
    if created:
        SignosVitales.objects.create(consulta=instance)
