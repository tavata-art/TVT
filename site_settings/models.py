from django.db import models
from django.utils.translation import gettext_lazy as _, gettext
from solo.models import SingletonModel

class SiteConfiguration(SingletonModel):
    """
    Singleton model to store site-wide configuration settings.
    Only one instance of this model will ever exist.
    """

    # --- Pagination Settings ---
    blog_posts_per_page = models.PositiveIntegerField(
        default=6, 
        verbose_name=_("Posts per Page in Blog")
    )
    search_results_per_page = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Results per Page in Search")
    )

    # --- Widget Settings ---
    recent_posts_widget_count = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Number of Posts in 'Recent Posts' Widget")
    )

    # --- ¡NUEVO CAMPO! ---
    popular_posts_widget_count = models.PositiveIntegerField(
        default=5, 
        verbose_name=_("Number of Posts in 'Most Viewed' Widget")
    )
    # --- We can add more settings in the future! ---
    # site_contact_email = models.EmailField(
    #     blank=True, 
    #     verbose_name=_("Site Contact Email")
    # )
    # maintenance_mode = models.BooleanField(
    #     default=False, 
    #     verbose_name=_("Maintenance Mode")
    # )

    class Meta:
        # This name will appear in the Django admin sidebar
        verbose_name = _("Site Configuration")
        # Django admin uses verbose_name_plural, but for a singleton, it's just one.
        verbose_name_plural = _("Site Configuration")

    def __str__(self):
        # The representation of the single object in the admin
        return gettext("Site Configuration")