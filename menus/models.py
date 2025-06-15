# menus/models.py
from django.db import models
from pages.models import Page # Importamos Page para poder enlazar a ellas

class MenuItem(models.Model):
    title = models.CharField(max_length=100, verbose_name="Título")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    
    # OPCIONES PARA EL ENLACE
    # El administrador podrá elegir una de estas tres opciones.
    url_externa = models.URLField(max_length=255, blank=True, null=True, verbose_name="URL Externa")
    pagina_interna = models.ForeignKey(Page, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Página Interna")
    url_especial = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        choices=[('list_categories', 'Listado de Categorías (Desplegable)')],
        verbose_name="Enlace Especial"
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Elemento de Menú"
        verbose_name_plural = "Elementos de Menú"

    def __str__(self):
        return self.title

    def get_url(self):
        if self.pagina_interna:
            return self.pagina_interna.get_absolute_url()
        elif self.url_externa:
            return self.url_externa
        # Si en el futuro tenemos más enlaces especiales, añadimos elif aquí.
        return "#" # URL por defecto si no hay nada definido
