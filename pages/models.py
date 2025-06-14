from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Definimos las opciones para el estado de publicación
STATUS_CHOICES = (
    ('draft', 'Borrador'),
    ('published', 'Publicada'),
)

class Page(models.Model):
    """
    Representa una página estática del CMS.
    """
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug (URL amigable)")
    content = models.TextField(verbose_name="Contenido")
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Autor")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "página"
        verbose_name_plural = "páginas"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Devuelve la URL canónica para una instancia de página.
        """
        return reverse('page_detail', kwargs={'slug': self.slug})