# File: categories/models.py
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    """
    A universal, hierarchical category model.
    It can be linked from other models via ForeignKey or ManyToManyField.
    """
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_("Parent Category")
    )
    description = models.TextField(
        blank=True, 
        verbose_name=_("Description"),
        help_text=_("An optional description for the category, can be shown on category pages.")
    )
    # --- SEO Fields ---
    meta_title = models.CharField(
        max_length=70, 
        blank=True, 
        verbose_name=_("Meta Title (SEO)"),
        help_text=_("A precise title for search engine results (max 70 chars).")
    )
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        verbose_name=_("Meta Description (SEO)"),
        help_text=_("A short description for search engine previews (max 160 chars).")
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{'--' * self.level} {self.name}"
    
    @property
    def is_for_blog(self):
        # A simple heuristic: if it's related to any blog post, it's a blog category.
        return self.blog_posts.exists()

    def get_absolute_url(self):
        # We need a way to know if this is a blog or page category to build the URL.
        # This is a challenge of a universal model. We will solve this later.
        # For now, let's return a placeholder.
        # A better solution would be to have different URL patterns based on some logic.
        # For now, we assume it's for the blog as it's the primary use case.
        if self.is_for_blog:
            return reverse('blog:posts_by_category', args=[self.slug])
        else:
            # Default to page categories.
            return reverse('pages:pages_by_category', args=[self.slug])