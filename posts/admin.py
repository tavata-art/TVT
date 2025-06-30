# File: posts/admin.py

import logging
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from parler.admin import TranslatableAdmin
from .models import Post
from tags.models import TaggedPost

logger = logging.getLogger(__name__)

class TaggedPostInline(admin.TabularInline):
    """
    🧩 Inline admin to manage tags assigned to a Post.
    Displays the related tag and optional relevance score.
    """
    model = TaggedPost
    extra = 1
    autocomplete_fields = ['tag']
    fields = ('tag', 'relevance_score')
    verbose_name = _("Assigned Tag")
    verbose_name_plural = _("Assigned Tags")

@admin.register(Post)
class PostAdmin(TranslatableAdmin):
    """
    🧠 Admin for multilingual Post model using django-parler.
    Combines inline tag editing and tag badge display.
    """

    # 📋 Columns shown in list view
    list_display = ('title', 'author', 'status', 'published_date', 'views_count', 'editor_rating', 'list_tags')
    list_filter = ('status', 'published_date', 'author')
    date_hierarchy = 'published_date'
    ordering = ('status', '-published_date')
    list_editable = ('status', 'editor_rating')

    # 🔍 Search across translated fields
    search_fields = (
        'translations__title',
        'translations__content',
        'translations__meta_title',
        'translations__meta_description'
    )

    # 🙈 Hidden fields in form
    exclude = ('author', 'views_count')

    # 🧩 Inline form for managing tag relations
    inlines = [TaggedPostInline]

    # 🏷 Visual badge list of tags
    @admin.display(description=_("Tags"))
    def list_tags(self, obj):
        tags = obj.tags.all()
        if tags:
            return format_html(' '.join([
                f'<span class="badge text-bg-warning">{tag.label}</span>' for tag in tags
            ]))
        return "-"

    # 🚀 Auto-assign author on creation
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
            logger.info(f"🆕 New post created by 🧑‍💻 {request.user.username}: {obj}")
        else:
            logger.info(f"✏️ Post updated by 🧑‍💻 {request.user.username}: {obj}")
        super().save_model(request, obj, form, change)
