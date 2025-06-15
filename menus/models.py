from django.db import models
from pages.models import Page

# ==============================================================================
# 1. EL NUEVO MODELO PARA AGRUPAR ENLACES
# ==============================================================================
class Menu(models.Model):
    """
    Representa una ubicación de menú en el sitio, como 'Menú Principal' o 'Menú del Footer'.
    """
    title = models.CharField(max_length=100, unique=True, verbose_name="Título del Menú")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug (identificador para el código)")

    class Meta:
        verbose_name = "Menú"
        verbose_name_plural = "Menús"

    def __str__(self):
        return self.title


# ==============================================================================
# 2. EL MODELO MenuItem EXISTENTE, AHORA MODIFICADO
# ==============================================================================
class MenuItem(models.Model):
    """
    Representa un enlace individual dentro de un Menú específico.
    """
    # --- ¡EL CAMPO CLAVE QUE AÑADIMOS! ---
    # Lo hacemos nulable temporalmente para que la migración no falle.
    menu = models.ForeignKey(
        Menu, 
        on_delete=models.CASCADE, 
        related_name="items", 
        verbose_name="Menú al que pertenece",
        null=True,  # <-- Permite que este campo esté vacío en la BD por ahora
        blank=True  # <-- Permite que este campo esté vacío en los formularios del admin
    )
    
    # --- Campos que ya tenías ---
    title = models.CharField(max_length=100, verbose_name="Texto del Enlace")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    
    link_page = models.ForeignKey(
        Page, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        verbose_name="Enlazar a una Página",
        help_text="Selecciona una página interna. Deja en blanco si usas una URL manual."
    )
    link_url = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Enlazar a una URL manual",
        help_text="Úsalo para URLs externas (ej: https://google.com) o rutas fijas (ej: /blog/)."
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Elemento de Menú"
        verbose_name_plural = "Elementos de Menú"

    def __str__(self):
        # Hacemos el __str__ un poco más informativo
        if self.menu:
            return f"{self.menu.title} - {self.title}"
        return self.title

    def get_url(self):
        if self.link_page:
            return self.link_page.get_absolute_url()
        if self.link_url:
            return self.link_url
        return "#"