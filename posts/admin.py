# File: posts/admin.py

import logging
from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Post
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

@admin.register(Post)
class PostAdmin(TranslatableAdmin):
    """
    🧠 Admin for multilingual Post model using django-parler tabs.
    Does not use any WYSIWYG editor. Keeps the interface clean.
    """

    # 📋 Columns displayed in the admin list view
    list_display = ('title', 'status', 'published_date', 'author')

    # 🔍 Sidebar filters
    list_filter = ('status', 'published_date')

    # 🙈 Hidden fields (set automatically or not relevant to edit)
    exclude = ('author', 'views_count')

    # 🔍 Searchable fields across all translations
    search_fields = (
        'translations__title',
        'translations__content',
        'translations__meta_title',
        'translations__meta_description'
    )

    # 🚀 Automatically assign author on post creation
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
            logger.info(f"🆕 New post created by 🧑‍💻 {request.user.username}: {obj}")
        else:
            logger.info(f"✏️ Post updated by 🧑‍💻 {request.user.username}: {obj}")
        super().save_model(request, obj, form, change)
