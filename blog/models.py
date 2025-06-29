# File: blog/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from categories.models import Category 
#from taggit.managers import TaggableManager
from django.utils.translation import override 

class Post(models.Model):
    """ Represents a single blog post. """

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        
    title = models.CharField(max_length=250, verbose_name=_("Title"))
    slug = models.SlugField(max_length=250, unique_for_date='published_date', verbose_name=_("Slug"))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name=_("Author"))
    
    content = models.TextField(verbose_name=_("Content"))
    featured_image = models.ImageField(
        upload_to='blog/featured/%Y/%m/%d/', 
        blank=True, 
        null=True, 
        verbose_name=_("Featured Image")
    )
    
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_("Published Date"))
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"))
    
    # --- CORRECTED CATEGORY RELATIONSHIP ---
    # Using a ManyToManyField is simpler and more efficient for querying than GenericRelation.
    categories = models.ManyToManyField(
        Category,
        blank=True,
        verbose_name=_("Categories"),
        related_name="blog_posts"
    )

    # --- SEO and Curation Fields ---
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Title (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Description (SEO)"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("View Count"))
    editor_rating = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Editor's Rating"),
        help_text=_("A score from 0-100 to feature this post. Higher numbers appear first.")
    )

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #tags = TaggableManager(
    #    verbose_name=_("Tags"),
    #    help_text=_("A comma-separated list of tags."),
    #    blank=True # Allows posts to have no tags
    #)

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
    
    def get_absolute_url_for_language(self, language_code):
        with override(language_code):
            # 'self.slug' automáticamente devuelve el slug para el idioma del contexto que acabamos de setear con override.
            return reverse('blog:post_detail', args=[
                self.published_date.year,
                self.published_date.month,
                self.published_date.day,
                self.slug
            ])


class Comment(MPTTModel):
    """ Represents a single, nestable comment on a blog post. """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_("Post"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True, verbose_name=_("Parent Comment"))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments_made', verbose_name=_("User"))
    author_name = models.CharField(max_length=100, blank=True, verbose_name=_("Author Name"))
    author_email = models.EmailField(blank=True, verbose_name=_("Author Email"))
    content = models.TextField(verbose_name=_("Content"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved?"))

    class MPTTMeta:
        order_insertion_by = ['created_at']

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        return f"{'--' * self.level} Comment by {self.get_author_name()}"
    
    def get_author_name(self):
        if self.user:
            return self.user.profile.get_display_name()
        return self.author_name

    def get_author_avatar_url(self):
        from django.templatetags.static import static
        if self.user and hasattr(self.user, 'profile') and self.user.profile.avatar:
            default_paths = [c[0] for c in self.user.profile.AvatarChoice.choices]
            if self.user.profile.avatar.name not in default_paths:
                return self.user.profile.avatar.url
            return static(self.user.profile.default_avatar_choice)
        
        return static('images/avatars/default_anonymous.png')