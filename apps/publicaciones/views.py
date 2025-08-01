from django.shortcuts import render
from .models import Publicacion


def obtener_publicaciones():
    """
    Función que devuelve las últimas publicaciones publicadas.
    Se puede importar en cualquier vista que necesite mostrar publicaciones.
    """
    return Publicacion.objects.filter(publicado=True).order_by('-fecha_publicacion')[:10]  # Últimas 10 publicaciones
