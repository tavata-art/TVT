from django.db import models
from django.utils.translation import gettext_lazy as _
from pages.models import Page

class Menu(models.Model):
    """
    Represents a menu location on the site, like 'Main Menu' or 'Footer Menu'.
    """
    title = models.CharField(max_length=100, unique=True, verbose_name=_("Menu Title"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug (identifier for code)"))

    class Meta:
        verbose_name = _("Menu")
        verbose_name_plural = _("Menus")

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    """
    Represents a single link item within a specific Menu.
    """
    menu = models.ForeignKey(
        Menu, 
        on_delete=models.CASCADE, 
        related_name="items", 
        verbose_name=_("Menu it belongs to"),
        # We keep these True for now to allow a smooth data migration.
        # Later, we can set them to False for data integrity.
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=100, verbose_name=_("Link Text"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    
    link_page = models.ForeignKey(
        Page, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        verbose_name=_("Link to a Page"),
        help_text=_("Select an internal page to link to. Leave blank if using a manual URL.")
    )
    link_url = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name=_("Link to a manual URL"),
        help_text=_("Use for external URLs (e.g., https://google.com) or fixed paths (e.g., /blog/).")
    )
    icon_class = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Icon Class (e.g., fab fa-facebook)"))

    class Meta:
        ordering = ['order']
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")

    def __str__(self):
        if self.menu:
            return f"{self.menu.title} - {self.title}"
        return self.title

    def get_url(self):
        if self.link_page:
            return self.link_page.get_absolute_url()
        if self.link_url:
            return self.link_url
        return "#"