# File: categories/templatetags/category_tags.py
import logging
from django import template
from django.core.cache import cache
from django.conf import settings
from ..models import Category

# Get a logger instance for this module
logger = logging.getLogger(__name__)

# This is necessary for Django to discover our custom tags
register = template.Library()


@register.inclusion_tag('categories/partials/_category_tree_component.html', takes_context=True)
def render_category_tree(context):
    """
    Fetches and renders the entire category tree.

    This tag is highly optimized:
    1. It's language-aware, caching a separate tree for each active language.
    2. It uses a configurable cache timeout, managed from the SiteConfiguration model.
    3. The cache is automatically invalidated by signals when a category is changed.
    """
    # 1. Get the current language from the template context to build a unique cache key.
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    cache_key = f'full_category_tree_nodes_{language_code}_v1'
    
    # 2. Try to fetch the full list of category nodes from the cache.
    nodes = cache.get(cache_key)
    
    # 3. If it's a "cache miss" (nodes is None), we query the database.
    if nodes is None:
        # We only log the DB query if caching was actually attempted (will be on a miss).
        logger.info(f"CACHE MISS for category tree (lang: {language_code}). Querying database.")
        
        # For `recursetree` to work efficiently, we fetch all nodes at once.
        # MPTT ensures they are correctly ordered for tree construction.
        nodes = Category.objects.all()
        
        # Evaluate to a list before caching to store the results, not the lazy queryset.
        nodes = list(nodes)

        # Get the cache timeout setting from our global site configuration.
        try:
            from site_settings.models import SiteConfiguration
            timeout = SiteConfiguration.objects.get().category_tree_cache_timeout
        except ImportError:
             logger.error("Could not import SiteConfiguration. Is the app in INSTALLED_APPS?")
             timeout = 3600 # Fallback to 1 hour
        except SiteConfiguration.DoesNotExist:
            logger.warning("SiteConfiguration not found. Using default cache timeout of 1 hour.")
            timeout = 3600 # Fallback to 1 hour
        
        # 4. Store the result in the cache if caching is enabled (timeout > 0).
        if timeout > 0:
            cache.set(cache_key, nodes, timeout)
            logger.debug(f"Cached category tree for {timeout} seconds.")
    else:
        logger.debug(f"CACHE HIT for category tree (lang: {language_code}). Serving from cache.")
            
    return {'nodes': nodes}