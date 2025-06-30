from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django.urls import reverse
from django.utils import timezone
from categories.models import Category 
from tags.models import Tag, TaggedPost

User = get_user_model()

class Post(TranslatableModel):
    """
    Represents a blog post with multilingual support using django-parler.
    This model is the central content unit in the 'posts' app.
    """

    translations = TranslatedFields(
        title=models.CharField(
            max_length=250,
            verbose_name=_("Title")
        ),
        slug=models.SlugField(
            max_length=250,
            unique=False,  # Parler handles uniqueness per language
            verbose_name=_("Slug")
        ),
        content=models.TextField(
            verbose_name=_("Content")
        ),
        meta_title=models.CharField(
            max_length=70,
            blank=True,
            null=True,
            verbose_name=_("Meta Title")
        ),
        meta_description=models.CharField(
            max_length=160,
            blank=True,
            null=True,
            verbose_name=_("Meta Description")
        )
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="translated_posts",
        verbose_name=_("Author")
    )

    featured_image = models.ImageField(
        upload_to='posts/featured/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_("Featured Image")
    )

    published_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Published Date")
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('draft', _("Draft")),
            ('published', _("Published")),
        ],
        default='draft',
        verbose_name=_("Status")
    )

    views_count = models.PositiveIntegerField(default=0, verbose_name=_("View Count"))
    editor_rating = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Editor's Rating"),
        help_text=_("A score from 0-100. Higher numbers can be used for ordering or editor’s picks.")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    tags = models.ManyToManyField(
        Tag,
        through=TaggedPost,
        related_name="posts",
        verbose_name=_("Tags"),
        blank=True,
        help_text=_("Tags assigned to this post. Managed via TaggedPost intermediate model."),
    )

    # --- CORRECTED CATEGORY RELATIONSHIP ---
    # Using a ManyToManyField is simpler and more efficient for querying than GenericRelation.
    categories = models.ManyToManyField(
        Category,
        blank=True,
        verbose_name=_("Categories"),
        related_name="posts_posts"
    )

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ['-published_date']

    def __str__(self):
        return str(self.safe_translation_getter("title", any_language=True) or _("(No title)"))


    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={
            'year': self.published_date.year,
            'month': self.published_date.month,
            'day': self.published_date.day,
            'slug': self.safe_translation_getter('slug', any_language=True)
        })
