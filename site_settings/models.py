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
    search_pages_per_page = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Pages per Page in Search Results")
    )
    search_posts_per_page = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Posts per Page in Search Results")
    )
    search_results_per_page = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Results per Page in Search"),
        help_text=_("Number of items to show per section (Pages/Posts) on the search results page.")
    )
    # --- Search Settings ---
    search_importance_limit = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Number of 'Important' Pages to show first in search"),
        help_text=_("How many top-priority pages to display before regular search results.")
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
        # --- Caching Settings ---
    menu_cache_timeout = models.PositiveIntegerField(
        default=3600, # Default to 1 hour (3600 seconds)
        verbose_name=_("Menu Cache Timeout (in seconds)"),
        help_text=_("How long the site menus should be stored in cache. Set to 0 to disable menu caching (not recommended).")
    )
    # --- Branding Settings ---
    site_logo = models.ImageField(
        upload_to='site_branding/',
        blank=True, null=True,
        verbose_name=_("Site Logo"),
        help_text=_("The main logo displayed in the top bar.")
    )
    site_slogan = models.CharField(
        max_length=150, 
        blank=True, 
        verbose_name=_("Site Slogan"),
        help_text=_("A short tagline displayed next to the logo.")
    )
    trusted_commenter_threshold = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Trusted Commenter Threshold"),
        help_text=_("The number of approved comments a user needs to post before their future comments are auto-approved.")
    )
    # --- Top Bar Banner/Ad Settings ---
    top_bar_banner_image = models.ImageField(
        upload_to='site_branding/banners/',
        blank=True, null=True,
        verbose_name=_("Top Bar Banner Image"),
        help_text=_("An optional banner image displayed in the top bar.")
    )
    top_bar_banner_link = models.URLField(
        max_length=255, 
        blank=True, 
        verbose_name=_("Top Bar Banner Link"),
        help_text=_("The URL the banner image will link to.")
    )

    class Meta:
        verbose_name = _("Site Configuration")
        verbose_name_plural = _("Site Configuration")

    def __str__(self):
        return gettext("Site Configuration")