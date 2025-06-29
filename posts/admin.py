# File: posts/admin.py

import logging
from django.contrib import admin
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
    autocomplete_fields = ['tag']  # Enables search-as-you-type for tag selection
    fields = ('tag', 'relevance_score')
    verbose_name = "Assigned Tag"
    verbose_name_plural = "Assigned Tags"


@admin.register(Post)
class PostAdmin(TranslatableAdmin):
    """
    🧠 Admin for multilingual Post model using django-parler tabs.
    Includes inline management of associated tags via TaggedPost.
    """
    list_display = ('title', 'status', 'published_date', 'author')
    list_filter = ('status', 'published_date')
    exclude = ('author', 'views_count')

    search_fields = (
        'translations__title',
        'translations__content',
        'translations__meta_title',
        'translations__meta_description'
    )

    inlines = [TaggedPostInline]  # 👈 Attach tag management here

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
            logger.info(f"🆕 New post created by 🧑\u200d💻 {request.user.username}: {obj}")
        else:
            logger.info(f"✏️ Post updated by 🧑\u200d💻 {request.user.username}: {obj}")
        super().save_model(request, obj, form, change)
