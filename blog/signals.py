# File: blog/signals.py
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User # For promoting trusted commenters

from .models import Post, Comment # Import Post and Comment for sender
from site_settings.models import SiteConfiguration # For cache timeouts and threshold from SiteConfiguration


logger = logging.getLogger(__name__)


# --- Signal to clear Widget caches on Post changes ---
@receiver([post_save, post_delete], sender=Post)
def clear_widget_caches_on_post_change(sender, instance, **kwargs):
    """
    Clears all widget caches related to posts whenever a Post is saved or deleted.
    This ensures that 'Recent Posts', 'Most Viewed', 'Editor's Picks' widgets are updated.
    """
    # Import Widget model specifically here to avoid circular dependency issues at startup
    from widgets.models import Widget 
    num_widgets_cleared = 0
    # A simple but effective strategy: clear ALL widget caches.
    # We iterate over all widgets that deal with posts.
    relevant_widget_types = ['recent_posts', 'tag_cloud_widget', 'most_viewed_posts', 'most_commented_posts', 'editor_picks_posts'] # Add other post-related widgets
    
    for widget in Widget.objects.filter(widget_type__in=relevant_widget_types): # Filter to relevant ones
        for lang_code, _ in settings.LANGUAGES: # Clear for each language
            cache_key = f'widget_items_{widget.id}_{lang_code}_v1' # Use 'v1'
            cache.delete(cache_key)
            num_widgets_cleared += 1
    logger.info(f"Cleared {num_widgets_cleared} widget caches due to Post change (ID: {instance.id}).")


# --- Signal for User Promotion to Trusted Commenter ---
@receiver(post_save, sender=Comment)
def promote_user_on_comment_approval(sender, instance, created, **kwargs):
    """
    Promotes a user to 'Trusted Commenter' status if they reach the configured
    threshold of approved comments. This signal runs when a Comment is saved.
    """
    # Only proceed if the comment is approved AND it's made by a registered user.
    if instance.is_approved and instance.user:
        try:
            # We import User's Profile here to avoid circular dependency at startup
            from accounts.models import Profile 
            user_profile = Profile.objects.get(user=instance.user)
            
            # Only promote if the user is not already trusted.
            if not user_profile.is_trusted_commenter:

                site_config = SiteConfiguration.get_solo()
                approval_threshold = getattr(site_config, 'trusted_commenter_threshold', 10) # Fallback to 10


                # Count all approved comments by this user.
                approved_comment_count = Comment.objects.filter(
                    user=instance.user, 
                    is_approved=True
                ).count()
                
                if approved_comment_count >= approval_threshold:
                    user_profile.is_trusted_commenter = True
                    user_profile.save(update_fields=['is_trusted_commenter'])
                    logger.info(f"User '{instance.user.username}' auto-promoted to Trusted Commenter (threshold: {approval_threshold} comments).")
        
        except Profile.DoesNotExist:
            logger.warning(f"Comment from user '{instance.user.username}' (ID: {instance.user.id}) has no associated Profile. Cannot check trusted status.")
        except Exception as e:
            logger.error(f"Unexpected error in promote_user_on_comment_approval for user '{instance.user.username}': {e}", exc_info=True)