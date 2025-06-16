from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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