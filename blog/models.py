# blog/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _ # Asegúrate de importar esto

# --- Modelo para las Categorías del Blog ---
class PostCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    # ¡NUEVOS CAMPOS SEO!
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=("Meta Título (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=("Meta Descripción (SEO)"))

    class Meta:
        verbose_name = _("categoría de blog")
        verbose_name_plural = "categorías de blog"
        ordering = ['name']

    def __str__(self):
        return self.name

# --- Modelo para las Entradas del Blog (Posts) ---
class Post(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    )

    title = models.CharField(max_length=250, verbose_name="Título")
    slug = models.SlugField(max_length=250, unique_for_date='published_date', verbose_name="Slug")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name="Autor")

    content = models.TextField(verbose_name="Contenido") # Lo dejaremos como TextField por ahora

    published_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Publicación")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")

    categories = models.ManyToManyField(PostCategory, related_name='posts', verbose_name="Categorías", blank=True)

    featured_image = models.ImageField(upload_to='blog/featured/%Y/%m/%d/', blank=True, null=True, verbose_name="Imagen Destacada")
    # ¡NUEVOS CAMPOS SEO!
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Título (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Descripción (SEO)"))
    class Meta:
        ordering = ('-published_date',)
        verbose_name = _("entrada de blog")
        verbose_name_plural = "entradas de blog"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[
            self.published_date.year,
            self.published_date.month,
            self.published_date.day,
            self.slug
        ])

