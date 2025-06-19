from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from categories.models import Category

class Page(models.Model):
    """ Represents a single static page in the CMS, like 'About Us'. """
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
    )
    
    title = models.CharField(max_length=250, verbose_name=_("Title"))
    slug = models.SlugField(max_length=250, unique=True, verbose_name=_("Slug (URL friendly)"))
    content = models.TextField(verbose_name=_("Content")) # The editor will be applied in admin.py
    
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="pages", verbose_name=_("Author"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name=_("Status"))
    
    categories = models.ManyToManyField(
        Category,
        blank=True,
        verbose_name=_("Categories"),
        related_name="pages"
    )
    
    is_homepage = models.BooleanField(
        default=False,
        verbose_name=_("Is Homepage?"),
        help_text=_("Mark only one page with this option. If multiple are marked, the most recent one will be used.")
    )

    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Title (SEO)"))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Description (SEO)"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation Date"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    importance_order = models.PositiveIntegerField(
        default=99,
        verbose_name=_("Importance Order"),
        help_text=_("A lower number means higher priority in search results. E.g., 1 for 'About Us', 2 for 'Contact', 99 for others.")
    )

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Uses the 'pages' namespace to generate the correct URL.
        return reverse('pages:page_detail', kwargs={'slug': self.slug})