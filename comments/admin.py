# File: comments/admin.py

import logging
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django.utils.translation import gettext_lazy as _
from .models import Comment

logger = logging.getLogger(__name__)

@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    """
    🧠 Admin panel for nested comments with moderation support.
    Inherits from MPTTModelAdmin to show threaded replies.
    """

    # 📋 Display in list view
    list_display = ('__str__', 'post', 'author_name', 'is_approved', 'created_at')
    list_display_links = ('__str__',)

    # 🎛️ Filters and editable fields
    list_filter = ('is_approved', 'created_at', 'post')
    list_editable = ('is_approved',)

    # 🔍 Search fields
    search_fields = ('content', 'author_name', 'author_email')

    # 🔒 Read-only fields for integrity
    readonly_fields = ('post', 'parent', 'user', 'author_name', 'author_email', 'content', 'created_at')

    @property
    def mptt_level_indent(self):
        """
        🧩 Optional: control indentation in tree display.
        Could be dynamic via SiteConfiguration in the future.
        """
        return 20  # You can update this to pull from config if needed

    def save_model(self, request, obj, form, change):
        """
        🧠 Logs changes and moderation actions.
        """
        super().save_model(request, obj, form, change)

        if not change:
            logger.info(f"🆕 New comment on '{obj.post}' by {obj.author_name or obj.user}")
        elif 'is_approved' in form.changed_data and obj.is_approved:
            logger.info(f"✅ Comment approved: id={obj.id} by {request.user}")
