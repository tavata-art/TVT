# widgets/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from blog.models import PostCategory
from pages.models import Category as PageCategory # Import with an alias to avoid name conflict

class WidgetZone(models.Model):
    """
    Defines a specific area in a template where widgets can be placed.
    e.g., 'Blog Sidebar', 'Footer Column 1', 'Homepage Sidebar'.
    """
    name = models.CharField(max_length=100, verbose_name=_("Zone Name"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug (used in templates)"))

    class Meta:
        verbose_name = _("Widget Zone")
        verbose_name_plural = _("Widget Zones")
        ordering = ['name']

    def __str__(self):
        return self.name


class Widget(models.Model):
    """
    Represents a single, configurable widget that can be placed in a WidgetZone.
    """
    class WidgetType(models.TextChoices):
        RECENT_POSTS = 'recent_posts', _('Recent Blog Posts')
        MOST_VIEWED_POSTS = 'most_viewed_posts', _('Most Viewed Blog Posts')
        MOST_COMMENTED_POSTS = 'most_commented_posts', _('Most Commented Blog Posts')
        BLOG_CATEGORIES = 'blog_categories', _('Blog Category List')
        # We can easily add more types in the future:
        # PAGE_LIST = 'page_list', _('List of Pages')
        # HTML_CONTENT = 'html_content', _('Custom HTML Content')

    zone = models.ForeignKey(
        WidgetZone, 
        on_delete=models.CASCADE, 
        related_name="widgets", 
        verbose_name=_("Widget Zone")
    )
    widget_type = models.CharField(
        max_length=50, 
        choices=WidgetType.choices, 
        verbose_name=_("Widget Type")
    )
    title = models.CharField(
        max_length=100, 
        verbose_name=_("Widget Title"),
        help_text=_("The title that will be displayed above the widget.")
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("Display Order")
    )
    
    # --- Configuration Fields (optional, used by specific widget types) ---
    item_count = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Number of items to show"),
        # Texto mejorado para reflejar su uso dual
        help_text=_("Used by widgets that display a list of items, like 'Recent Posts' or 'Blog Categories'.")
    )
    
    blog_category_filter = models.ForeignKey(
        PostCategory, 
        null=True, blank=True, 
        on_delete=models.SET_NULL, 
        verbose_name=_("Filter by Blog Category (optional)"),
        help_text=_("If selected, the widget will only show posts from this category.")
    )

    page_category_filter = models.ForeignKey(
        PageCategory,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Filter by Page Category (optional)"),
        help_text=_("Used for a future 'List of Pages' widget.")
    )

    class Meta:
        ordering = ['zone', 'order']
        verbose_name = _("Widget")
        verbose_name_plural = _("Widgets")

    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()}) in {self.zone.name}"

# Create your models here.
