# File: blog/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        """
        Connects signals and explicitly registers ModelAdmins for third-party apps.
        """
        import blog.signals # Connects blog signals
        
        # --- Explicitly register our custom TagAdmin. ---
        try:
            from django.contrib import admin
            from taggit.models import Tag
            from .admin import TagAdmin # Import our custom TagAdmin from blog/admin.py

            # Check if default TagAdmin is already registered (it normally is by taggit).
            if admin.site.is_registered(Tag): 
                admin.site.unregister(Tag) # Unregister the default one.
                logger.info("Unregistered default Taggit TagAdmin.")
            
            # Register our custom TagAdmin.
            admin.site.register(Tag, TagAdmin) 
            logger.debug("Successfully registered custom Blog app's TagAdmin.")

        except Exception as e:
            logger.error(f"Error registering custom TagAdmin: {e}", exc_info=True)
            # Log the error but don't re-raise, so Django can continue loading other apps.
            # If this becomes a problem, consider re-raising.