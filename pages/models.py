from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # En el futuro, podríamos tener una página que liste todas las páginas de una categoría
        return reverse('pages_by_category', args=[self.slug])

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
    # ¡NUEVO CAMPO! La relación con Categorías.
    # Usamos ManyToManyField porque una página puede estar en varias categorías,
    # y una categoría puede tener varias páginas.
    categories = models.ManyToManyField(
        Category, 
        verbose_name="Categorías", 
        related_name="pages", # Nos permite hacer category.pages para obtener las páginas
        blank=True # Hace que asignar una categoría no sea obligatorio
    )
    
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