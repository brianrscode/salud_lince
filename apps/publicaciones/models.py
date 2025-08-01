from django.db import models
from django.utils import timezone
from apps.usuarios.models import Usuario

class Publicacion(models.Model):
    titulo = models.CharField('Título', max_length=200)
    # contenido = models.TextField('Contenido')
    imagen = models.ImageField('Imagen', upload_to='publicaciones/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField('Fecha de publicación', default=timezone.now)
    autor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    publicado = models.BooleanField('Publicado', default=True)

    class Meta:
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo
