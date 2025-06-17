from django.db import models
from django.utils.translation import gettext_lazy as _, gettext
from solo.models import SingletonModel

class SiteConfiguration(SingletonModel):
    """
    Singleton model to store site-wide configuration settings.
    Only one instance of this model will ever exist.
    """

    # --- Pagination Settings ---
    blog_items_per_page = models.PositiveIntegerField(
        default=9, 
        verbose_name=_("Items per Page in Blog/Category lists"),
        help_text=_("Number of posts to show on the main blog page and on category pages.")
    )
    search_results_per_page = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Results per Page in Search"),
        help_text=_("Number of items to show per section (Pages/Posts) on the search results page.")
    )

    # --- Widget Settings ---
    recent_posts_widget_count = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Number of Posts in 'Recent Posts' Widget")
    )

    popular_posts_widget_count = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Number of Posts in 'Most Viewed' Widget")
    )

    # --- Admin Display Settings ---
    comment_indentation_pixels = models.PositiveIntegerField(
        default=20,
        verbose_name=_("Comment Indentation (in pixels)"),
        help_text=_("Controls the visual indentation for nested comments in the admin.")
    )

    # --- Comment Moderation Settings ---
    auto_approve_comments = models.BooleanField(
        default=False, 
        verbose_name=_("Auto-approve comments"),
        help_text=_("If checked, new comments will be published immediately without moderation.")
    )

    class Meta:
        verbose_name = _("Site Configuration")
        verbose_name_plural = _("Site Configuration")

    def __str__(self):
        return gettext("Site Configuration")