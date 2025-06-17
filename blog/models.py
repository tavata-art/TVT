from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey # ¡Importamos las herramientas de mptt!

class PostCategory(models.Model):
    """ Represents a category for grouping blog posts. """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Title (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Description (SEO)"))

    class Meta:
        verbose_name = _("blog category")
        verbose_name_plural = _("blog categories")
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Generates the URL to list all posts in this category.
        return reverse('blog:posts_by_category', args=[self.slug])


class Post(models.Model):
    """ Represents a single blog post. """

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        
    title = models.CharField(max_length=250, verbose_name=_("Title"))
    slug = models.SlugField(max_length=250, unique_for_date='published_date', verbose_name=_("Slug"))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name=_("Author"))
    
    content = models.TextField(verbose_name=_("Content"))
    featured_image = models.ImageField(upload_to='blog/featured/%Y/%m/%d/', blank=True, null=True, verbose_name=_("Featured Image"))
    
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_("Published Date"))
    
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"))
    
    categories = models.ManyToManyField(PostCategory, related_name='posts', verbose_name=_("Categories"), blank=True)

    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Title (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Description (SEO)"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # For tracking the number of views
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("View Count"))
    class Meta:
        ordering = ('-published_date',)
        verbose_name = _("blog post")
        verbose_name_plural = _("blog posts")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[
            self.published_date.year,
            self.published_date.month,
            self.published_date.day,
            self.slug
        ])
    
# --- NEW, NESTABLE COMMENT MODEL ---
class Comment(MPTTModel):
    """
    Represents a single, nestable comment on a blog post.
    Inherits from MPTTModel to handle the tree structure.
    """
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        verbose_name=_("Post")
    )
    
    # The 'parent' field allows for nested comments (replies).
    # TreeForeignKey is a special field from django-mptt.
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        db_index=True,
        verbose_name=_("Parent Comment")
    )
    
    # We allow anonymous comments, so we store the name and email directly.
    author_name = models.CharField(max_length=100, verbose_name=_("Author Name"))
    author_email = models.EmailField(verbose_name=_("Author Email"))
    
    content = models.TextField(verbose_name=_("Content"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    # This is crucial for moderation.
    # We'll set the default to True for easier testing. Change to False for production.
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved?"))
    

    class MPTTMeta:
        # This tells django-mptt how to order the comments within the tree structure.
        # Here, we order by the creation date to show comments chronologically.
        order_insertion_by = ['-created_at']

    class Meta:
        # The default ordering is now handled by MPTTMeta, so we can remove it from here.
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        # A small visual trick to show the comment's nesting level in the admin list.
        # 'self.level' is a field automatically provided by mptt.
        return f"{'--' * self.level} Comment by {self.author_name}"
