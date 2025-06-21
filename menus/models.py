# File: menus/models.py
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Third-party imports
from mptt.models import MPTTModel, TreeForeignKey

# Local application imports (ensure these models exist in pages.models and categories.models)
from pages.models import Page # For linking to specific internal pages
# from categories.models import Category # If Category is needed for direct link types


class Menu(models.Model):
    """
    Represents a container for menu items, defining a specific menu location.
    Examples: 'Main Menu', 'Footer Menu', 'Social Media Links'.
    """
    title = models.CharField(max_length=100, unique=True, verbose_name=_("Menu Title"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))

    class Meta:
        verbose_name = _("Menu")
        verbose_name_plural = _("Menus")

    def __str__(self):
        # Modeltranslation automatically provides the translated title.
        return self.title


class MenuItem(MPTTModel):
    """
    Represents a single, hierarchical item within a specific Menu.
    It can be a simple link, or a dynamic placeholder that generates sub-items
    (e.g., a "Blog Categories" dropdown).
    """

    # Enum for defining the type of link this menu item represents.
    class LinkType(models.TextChoices):
        URL = 'url', _('Manual URL')
        PAGE = 'page', _('Single Page')
        # These types are placeholders for dynamic content generation in the frontend.
        ALL_BLOG_CATEGORIES = 'all_blog_categories', _('Blog Categories Tree (Dropdown)')
        IMPORTANT_PAGES = 'important_pages', _('Important Pages List (Dropdown)')

    # --- Core Relationships ---
    # The Menu container this item belongs to.
    menu = models.ForeignKey(
        Menu, 
        on_delete=models.CASCADE, 
        related_name="items", 
        verbose_name=_("Menu")
    )
    
    # The 'parent' field enables hierarchical (nested) menu structures,
    # provided by django-mptt.
    parent = TreeForeignKey(
        'self', # Refers to the MenuItem model itself.
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        db_index=True, # For efficient lookups.
        verbose_name=_("Parent Menu Item"),
        help_text=_("Select a parent item to nest this menu item within it.")
    )
    
    # --- Item Content and Order ---
    title = models.CharField(max_length=100, verbose_name=_("Link Text"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))

    # --- Link Configuration ---
    # Specifies how the menu item will generate its URL or dynamic content.
    link_type = models.CharField(
        max_length=50, # Sufficient for all TextChoices values.
        choices=LinkType.choices,
        default=LinkType.URL,
        verbose_name=_("Link Type"),
        help_text=_("Determines how this menu item behaves: a direct link, or a dynamic content generator.")
    )

    # Conditional link fields. Only one of these should typically be filled.
    link_page = models.ForeignKey(
        Page, 
        on_delete=models.SET_NULL, # If the page is deleted, the menu item link becomes null.
        null=True, 
        blank=True, 
        verbose_name=_("Page Link"),
        help_text=_("Link to a specific internal page. Only used if Link Type is 'Single Page'.")
    )
    link_url = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name=_("Manual URL"),
        help_text=_("Use for external URLs (e.g., 'https://google.com') or custom internal paths (e.g., '/blog/'). Only used if Link Type is 'Manual URL'.")
    )
    icon_class = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Icon Class"),
        help_text=_("FontAwesome class (e.g., 'fas fa-home') to display an icon next to the link.")
    )

    class MPTTMeta:
        """ MPTT specific options for ordering nodes within the tree. """
        order_insertion_by = ['order'] # Orders items by their 'order' field.

    class Meta:
        """ Standard Django model metadata. """
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        # Ensure consistent display order for all queries by default.
        ordering = ['order'] 

    def __str__(self):
        """ Returns an indented string representation useful for admin display. """
        # 'self.level' is automatically provided by django-mptt.
        return f"{'--' * self.level} {self.title}"

    def get_url(self):
        """
        Generates the actual URL for the menu item based on its link_type.
        Returns a placeholder '#' if no valid URL is configured.
        """
        if self.link_type == self.LinkType.PAGE and self.link_page:
            return self.link_page.get_absolute_url()
        elif self.link_type == self.LinkType.URL and self.link_url:
            return self.link_url
        # For dynamic link types (like ALL_BLOG_CATEGORIES) the URL is often '#'
        # as clicking the top-level item expands the dropdown, not navigates.
        return "#"
