# File: publications/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django.urls import reverse
from django.utils import timezone
from categories.models import Category
from tinymce.models import HTMLField
from django.utils.translation import get_language

User = get_user_model()

class Publication(TranslatableModel):
    """
    📄 Represents a scientific or academic publication, designed for long-term preservation and export.
    """

    # 🔤 Translatable Fields
    translations = TranslatedFields(
        title=models.CharField(max_length=250, verbose_name=_("Title")),
        slug=models.SlugField(max_length=250, unique=False, verbose_name=_("Slug")),
        abstract=models.TextField(blank=True, verbose_name=_("Abstract")),
        content=HTMLField(verbose_name=_("Full Content")),
        meta_title=models.CharField(max_length=70, blank=True, null=True, verbose_name=_("Meta Title")),
        meta_description=models.CharField(max_length=160, blank=True, null=True, verbose_name=_("Meta Description")),
    )

    # 🔗 Core Relations
    authors = models.ManyToManyField(User, related_name="publications", verbose_name=_("Authors"))
    categories = models.ManyToManyField(Category, blank=True, related_name="publications", verbose_name=_("Categories"))

    # 📚 Academic Metadata
    doi = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("DOI"))

    # 🖼️ Media & Files
    featured_image = models.ImageField(upload_to='publications/featured/', blank=True, null=True, verbose_name=_("Cover Image"))
    attachment = models.FileField(upload_to='publications/files/', blank=True, null=True, verbose_name=_("Full PDF"))

    # 🕒 Timeline
    publication_date = models.DateField(default=timezone.now, verbose_name=_("Publication Date"))
    is_published = models.BooleanField(default=False, verbose_name=_("Is Published?"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Publication")
        verbose_name_plural = _("Publications")
        ordering = ['-publication_date']

    def __str__(self):
        title = self.safe_translation_getter("title", any_language=True)
        return str(title) if title else str(_("Untitled"))

    def get_absolute_url(self):
        return reverse('publications:publication_detail', kwargs={
            'slug': self.safe_translation_getter("slug", any_language=True)
        })
    
    def get_authors_display(self):
        return ", ".join([a.get_full_name() or a.username for a in self.authors.all()])

    # 📂 Categories display logic
    def get_categories_display(self):
        lang = get_language()
        return ", ".join([
            getattr(cat, f"name_{lang}", cat.name) for cat in self.categories.all()
        ])
