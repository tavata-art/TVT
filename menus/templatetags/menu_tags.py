# File: menus/templatetags/menu_tags.py
import logging
from django import template
from django.core.cache import cache
from django.conf import settings
from ..models import Menu

logger = logging.getLogger(__name__)
register = template.Library()


@register.inclusion_tag('menus/render_menu.html', takes_context=True)
def show_menu(context, menu_slug):
    """
    Renders a specific menu by its slug, utilizing a configurable cache.
    The cache key is language-aware to support multilingual menus.
    """
    # Get the current language from the template context, defaulting to the site's default.
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    
    # 1. Create a unique, versioned, and language-specific cache key.
    cache_key = f'menu_items_{menu_slug}_{language_code}_v1'
    
    # 2. Try to fetch the menu items from the cache.
    menu_items = cache.get(cache_key)
    
    # 3. If it's a "cache miss" (items are not in cache), query the database.
    if menu_items is None:
        try:
            # We only need the SiteConfiguration to get the cache timeout.
            # We import it here to avoid circular dependency issues at startup.
            from site_settings.models import SiteConfiguration
            config = SiteConfiguration.objects.get()
            timeout = config.menu_cache_timeout
        except SiteConfiguration.DoesNotExist:
            timeout = 3600  # Fallback to 1 hour if config is not set.
            logger.warning(f"SiteConfiguration not found. Using default menu cache timeout of {timeout}s.")

        logger.info(f"CACHE MISS for menu '{menu_slug}' in language '{language_code}'. Querying database.")
        
        try:
            menu = Menu.objects.prefetch_related('items').get(slug=menu_slug)
            # Evaluate the queryset to a list before caching to store the actual results.
            menu_items = list(menu.items.all())
                
            # 4. Store the result in the cache if caching is enabled (timeout > 0).
            if timeout > 0:
                cache.set(cache_key, menu_items, timeout)
                
        except Menu.DoesNotExist:
            logger.warning(f"Menu with slug '{menu_slug}' does not exist.")
            menu_items = []
    
    else:
        logger.debug(f"CACHE HIT for menu '{menu_slug}' in language '{language_code}'. Serving from cache.")

    return {'menu_items': menu_items}


@register.inclusion_tag('menus/social_links_menu.html')
def show_social_links():
    """
    A dedicated tag to render the social media links menu.
    It's a simplified version of show_menu for a fixed slug.
    """
    # The cache key for social links doesn't need to be language-specific
    # as icons are universal.
    cache_key = 'social_links_menu_v1'
    menu_items = cache.get(cache_key)

    if menu_items is None:
        try:
            from site_settings.models import SiteConfiguration
            timeout = SiteConfiguration.objects.get().menu_cache_timeout
        except SiteConfiguration.DoesNotExist:
            timeout = 3600 # Fallback

        logger.info(f"CACHE MISS for 'social-links' menu. Querying database.")
        
        try:
            menu = Menu.objects.get(slug='social-links')
            menu_items = list(menu.items.all())
            if timeout > 0:
                cache.set(cache_key, menu_items, timeout)

        except Menu.DoesNotExist:
            logger.warning("Menu with slug 'social-links' does not exist. Cannot display social media icons.")
            menu_items = []
    else:
        logger.debug(f"CACHE HIT for 'social-links' menu. Serving from cache.")

    return {'menu_items': menu_items}