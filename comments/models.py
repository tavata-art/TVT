# File: comments/models.py

from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext_lazy as _
from posts.models import Post  # 👈 Ajusta si cambia el nombre del modelo o app
from django.utils import timezone

User = get_user_model()

class Comment(MPTTModel):
    """
    🗨️ Represents a nested, user-submitted comment.
    Includes moderation, translation metadata and nesting (via MPTT).
    """

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

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments_made_by',
        verbose_name=_("User")
    )

    author_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Author Name")
    )

    author_email = models.EmailField(
        blank=True,
        verbose_name=_("Author Email")
    )

    content = models.TextField(verbose_name=_("Content"))
    language = models.CharField(max_length=10, default='en', verbose_name=_("Original Language"))

    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved?"))

    # 🈯️ Translation metadata
    translated_content = models.TextField(blank=True, null=True, verbose_name=_("Translated Content"))
    translated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="translated_comments",
        verbose_name=_("Translated by"),
        help_text=_("User who provided the translation, if different from the author.")
    )
    translation_language = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_("Translation Language")
    )

    class MPTTMeta:
        order_insertion_by = ['created_at']

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        lang_note = f"[{self.language}]" if self.language else ""
        return f"{'—' * self.level} {self.get_display_author()} {lang_note}"

    def get_display_author(self):
        return self.user.profile.get_display_name() if self.user else self.author_name

    def get_display_content(self, preferred_language=None):
        """
        💬 Returns translated content if applicable and requested.
        """
        if preferred_language and preferred_language == self.translation_language and self.translated_content:
            return self.translated_content
        return self.content
