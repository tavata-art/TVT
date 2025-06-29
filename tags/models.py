# File: tags/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

class Tag(TranslatableModel):
    """
    🐝 Multilingual Tag model for categorizing content.
    """
    translations = TranslatedFields(
        label=models.CharField(max_length=250, verbose_name=_("Label"))
    )
    slug = models.SlugField(unique=True, max_length=250, verbose_name=_("Slug"))

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.safe_translation_getter("label", any_language=True)


class TaggedPost(models.Model):
    """
    🧩 Through model linking Tags to Posts, with optional metadata.
    """
    post = models.ForeignKey(
        'posts.Post',  # ✅ Usamos una referencia perezosa por string
        on_delete=models.CASCADE,
        related_name="tag_links",
        verbose_name=_("Post"),
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="post_links",
        verbose_name=_("Tag"),
    )

    relevance_score = models.PositiveIntegerField(
        default=100,
        verbose_name=_("Relevance Score"),
        help_text=_("Optional score from 0 to 100 indicating tag relevance."),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Assigned At"))

    class Meta:
        unique_together = ("post", "tag")
        verbose_name = _("Tagged Post")
        verbose_name_plural = _("Tagged Posts")

    def __str__(self):
        return f"{self.tag} → {self.post}"
