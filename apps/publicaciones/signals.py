import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Publicacion


@receiver(post_delete, sender=Publicacion)
def eliminar_imagen_al_eliminar_publicacion(sender, instance, **kwargs):
    if instance.imagen:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)


@receiver(pre_save, sender=Publicacion)
def eliminar_imagen_anterior_si_se_reemplaza(sender, instance, **kwargs):
    if not instance.pk:
        return  # La publicación es nueva, no hay imagen anterior

    try:
        publicacion_anterior = Publicacion.objects.get(pk=instance.pk)
    except Publicacion.DoesNotExist:
        return

    imagen_anterior = publicacion_anterior.imagen
    nueva_imagen = instance.imagen

    if imagen_anterior and imagen_anterior != nueva_imagen:
        if os.path.isfile(imagen_anterior.path):
            os.remove(imagen_anterior.path)
