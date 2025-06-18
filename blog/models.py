from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey 
from django.conf import settings

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
    
# --- NESTABLE COMMENT MODEL WITH USER INTEGRATION ---
class Comment(MPTTModel):
    """
    Represents a single, nestable comment on a blog post.
    A comment can be posted by a registered user or an anonymous guest.
    """
    # === Core Relationships ===
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        verbose_name=_("Post")
    )
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        db_index=True,
        verbose_name=_("Parent Comment")
    )
    
    # === Author Information ===
    # This field links to a registered user. It's optional for guest comments.
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # If user is deleted, keep the comment as anonymous
        null=True, 
        blank=True,
        related_name='comments_made', 
        verbose_name=_("User")
    )
    # These fields are required for guest comments, but can be auto-filled for registered users.
    author_name = models.CharField(max_length=100, verbose_name=_("Author Name"), blank=True)
    author_email = models.EmailField(verbose_name=_("Author Email"), blank=True)
    
    # === Comment Content & Status ===
    content = models.TextField(verbose_name=_("Content"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    is_approved = models.BooleanField(
        default=False, # Default to False for production to enable moderation
        verbose_name=_("Is Approved?")
    )

    class MPTTMeta:
        # This tells django-mptt how to order comments within the tree.
        # Oldest comments will appear first.
        order_insertion_by = ['created_at']

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        # A visual trick to show nesting levels in the admin.
        return f"{'--' * self.level} Comment by {self.author_name} on \"{self.post.title[:20]}...\""
    
    # --- Helper Methods for Templates ---
    def get_author_name(self):
        """
        Returns the author's display name, preferring the registered user's profile.
        """
        if self.user and hasattr(self.user, 'profile'):
            return self.user.profile.get_display_name()
        return self.author_name

    def get_author_avatar_url(self):
        """
        Returns the author's avatar URL.
        Falls back to a generic anonymous avatar if the user is not registered or has no avatar.
        """
        # Define a fallback URL for a generic guest avatar
        # You must create this image and place it in your static files.
        anonymous_avatar_url = f"{settings.STATIC_URL}images/avatars/default_anonymous.png"

        if self.user and hasattr(self.user, 'profile') and self.user.profile.avatar:
            # Check if the user has a custom avatar uploaded
            if self.user.profile.avatar.name != self.user.profile._meta.get_field('avatar').get_default():
                return self.user.profile.avatar.url
            # If not, return the user's chosen default avatar
            return f"{settings.STATIC_URL}{self.user.profile.avatar.name}"
        
        # If all else fails, return the anonymous avatar
        return anonymous_avatar_url