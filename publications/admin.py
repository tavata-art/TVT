# File: publications/admin.py

import logging
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from django.utils.translation import get_language

from .models import Publication

logger = logging.getLogger(__name__)


@admin.register(Publication)
class PublicationAdmin(TranslatableAdmin):
    """
    📚 Admin for multilingual Publication model using django-parler.
    Optimized for academic/research-style documents.
    """

    # 📋 Columns shown in list view
    list_display = ('title', 'get_authors', 'is_published', 'publication_date', 'get_categories')
    list_filter = ('is_published', 'publication_date', 'authors')
    ordering = ('-publication_date',)
    date_hierarchy = 'publication_date'

    # 🔍 Search in translations and DOI
    search_fields = (
        'translations__title',
        'translations__abstract',
        'translations__meta_title',
        'translations__meta_description',
        'doi',
    )

    # 🧮 Select multiple authors and categories with UI
    filter_horizontal = ('authors', 'categories')

    # 🙈 Optional: hide auto fields
    readonly_fields = ('created_at', 'updated_at')

    # ✍️ Group fields in the form
    fieldsets = (
        (_("Main Information"), {
            'fields': ('title', 'slug', 'abstract', 'content')
        }),
        (_("Metadata & SEO"), {
            'fields': ('meta_title', 'meta_description', 'doi', 'publication_date', 'is_published')
        }),
        (_("Relations"), {
            'fields': ('authors', 'categories')
        }),
        (_("Media & Files"), {
            'fields': ('featured_image', 'attachment')
        }),
        (_("System Info"), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # 🧑‍🏫 Author display logic
    @admin.display(description=_("Authors"))
    def get_authors(self, obj):
        return ", ".join([a.get_full_name() or a.username for a in obj.authors.all()])

    # 📂 Categories display logic
    def get_categories(self, obj):
        language = get_language()
        name_field = f"name_{language}"
        return ", ".join([getattr(c, name_field, c.name) for c in obj.categories.all()])


    # 🧠 Optional: Auto log
    def save_model(self, request, obj, form, change):
        logger.info(f"{'🆕' if not change else '✏️'} Publication saved by {request.user.username}: {obj}")
        super().save_model(request, obj, form, change)
