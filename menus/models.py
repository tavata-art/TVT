# menus/models.py
from django.db import models
from pages.models import Page

class MenuItem(models.Model):
    title = models.CharField(max_length=100, verbose_name="Texto del Enlace")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    # El administrador solo llenará uno de estos dos campos.
    link_page = models.ForeignKey(
        Page, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        verbose_name="Enlazar a una Página",
        help_text="Selecciona una página interna para enlazar. Deja en blanco si usas una URL manual."
    )
    link_url = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Enlazar a una URL manual",
        help_text="Usa esto para URLs externas (ej: https://google.com) o rutas manuales (ej: /blog/)."
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Elemento de Menú"
        verbose_name_plural = "Elementos de Menú"

    def __str__(self):
        return self.title

    def get_url(self):
        if self.link_page:
            return self.link_page.get_absolute_url()
        elif self.link_url:
            return self.link_url
        return "#" # URL de respaldo
