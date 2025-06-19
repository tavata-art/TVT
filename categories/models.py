# File: categories/models.py
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    """
    A universal, hierarchical category model using a simple self-referencing
    ForeignKey to handle nesting.
    """
    # Basic category fields
    name = models.CharField(
        max_length=100, 
        verbose_name=_("Name")
    )
    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Slug")
    )
    
    # Simple hierarchy field
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_("Parent Category"),
        help_text=_("Select a parent to create a sub-category.")
    )
    
    # Optional descriptive fields
    description = models.TextField(
        blank=True, 
        verbose_name=_("Description"),
        help_text=_("An optional description for the category.")
    )
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=70, 
        blank=True, null=True,
        verbose_name=_("Meta Title (SEO)"),
        help_text=_("A precise title for search engine results (max 70 chars).")
    )
    meta_description = models.CharField(
        max_length=160, 
        blank=True, null=True,
        verbose_name=_("Meta Description (SEO)"),
        help_text=_("A short description for search engine previews (max 160 chars).")
    )

    class Meta:
        """ Standard Django model metadata. """
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        # Order alphabetically by default in the admin and queries.
        ordering = ['name']

    def __str__(self):
        """ Provides a clear representation in the admin, showing hierarchy. """
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name
    
    @property
    def is_blog_category(self):
        """ Checks if this category is used for blog posts. """
        return hasattr(self, 'blog_posts') and self.blog_posts.exists()

    def get_absolute_url(self):
        """
        Generates the correct URL for the category's list page.
        """
        if self.is_blog_category:
            return reverse('blog:posts_by_category', args=[self.slug])
        else:
            # Fallback to the pages category list view
            return reverse('pages:pages_by_category', args=[self.slug])