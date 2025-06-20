# File: menus/models.py
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from pages.models import Page

class Menu(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name=_("Menu Title"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))

    class Meta:
        verbose_name = _("Menu")
        verbose_name_plural = _("Menus")

    def __str__(self):
        return self.title

class MenuItem(MPTTModel):
    class LinkType(models.TextChoices):
        URL = 'url', _('Manual URL')
        PAGE = 'page', _('Single Page')
        ALL_BLOG_CATEGORIES = 'all_blog_categories', _('Blog Categories Tree (Dropdown)')
        IMPORTANT_PAGES = 'important_pages', _('Important Pages List (Dropdown)')

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items", verbose_name=_("Menu"))
    
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children',
        verbose_name=_("Parent Menu Item")
    )
    
    title = models.CharField(max_length=100, verbose_name=_("Link Text"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))

    link_type = models.CharField(
        max_length=50,
        choices=LinkType.choices,
        default=LinkType.URL,
        verbose_name=_("Link Type")
    )

    link_page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Page Link"))
    link_url = models.CharField(max_length=255, blank=True, verbose_name=_("Manual URL"))
    icon_class = models.CharField(max_length=100, blank=True, verbose_name=_("Icon Class"))

    class MPTTMeta:
        order_insertion_by = ['order']

    class Meta:
        verbose_name=_("Menu Item")
        verbose_name_plural=_("Menu Items")

    def __str__(self):
        return f"{'--' * self.level} {self.title}"

    def get_url(self):
        if self.link_type == 'page' and self.link_page:
            return self.link_page.get_absolute_url()
        elif self.link_type == 'url':
            return self.link_url
        return "#"