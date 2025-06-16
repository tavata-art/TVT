from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")

    # ¡AÑADIMOS LOS CAMPOS SEO!
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Título (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Descripción (SEO)"))

    class Meta:
        verbose_name = _("categoría de página")
        verbose_name_plural = _("categorías de página")
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
    # --- NUEVO CAMPO ---
    is_homepage = models.BooleanField(
        default=False,
        verbose_name="¿Es la página de inicio?",
        help_text="Marcar solo una página con esta opción. Si varias están marcadas, se usará la más reciente."
    )
    # ¡AÑADIMOS LOS CAMPOS SEO!
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Título (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Descripción (SEO)"))

    class Meta:
        verbose_name = _("página")
        verbose_name_plural = _("páginas")
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Ahora usamos 'namespace:nombre_de_la_ruta'
        return reverse('pages:page_detail', kwargs={'slug': self.slug})