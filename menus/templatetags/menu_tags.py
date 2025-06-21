# File: menus/templatetags/menu_tags.py
import logging
from django import template
from django.core.cache import cache
from django.conf import settings # Needed for settings.LANGUAGES and settings.LANGUAGE_CODE
from django.db.models import Count, Q # Needed for dynamic children queries

# Import necessary models for the dynamic logic
from ..models import Menu, MenuItem # Relative import for models within the same app
from pages.models import Page # For Important Pages list
from categories.models import Category # For Blog Categories list

# Import SiteConfiguration for cache timeout settings (handle potential ImportError or DoesNotExist)
try:
    from site_settings.models import SiteConfiguration
except ImportError:
    logger.error("Could not import SiteConfiguration. Ensure 'site_settings' app is in INSTALLED_APPS.")
    SiteConfiguration = None # Fallback for type hinting / future handling

logger = logging.getLogger(__name__) # Get logger specific to this module
register = template.Library() # Register this as a Django template library


@register.inclusion_tag('menus/partials/_navbar_recursive.html', takes_context=True)
def show_menu(context, menu_slug):
    """
    Fetches and renders a full menu tree by its slug.
    It utilizes a configurable cache and handles dynamically generating sub-items
    for special menu item types (e.g., categories tree, important pages).
    """
    # 1. Determine current language for cache key (ensures language-aware caching)
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    
    # 2. Define a unique and versioned cache key for this specific menu and language.
    cache_key = f'menu_nodes_{menu_slug}_{language_code}_v1' # Increment v1 to v2 to invalidate all caches

    # 3. Try to fetch the processed menu items from the cache first.
    menu_items_processed = cache.get(cache_key)

    if menu_items_processed is None:
        logger.info(f"CACHE MISS for menu '{menu_slug}' (lang: {language_code}). Building menu tree.")

        # Get SiteConfiguration for cache timeout and dynamic content limits
        site_config = None
        try:
            site_config = SiteConfiguration.objects.get()
            timeout = site_config.menu_cache_timeout
        except SiteConfiguration.DoesNotExist:
            timeout = 3600 # Fallback 1 hour
            logger.warning("SiteConfiguration not found. Using default menu cache timeout of 3600s.")
        except AttributeError: # Handles case if SiteConfiguration was not imported
            timeout = 3600
            logger.warning("SiteConfiguration model not accessible. Using default menu cache timeout of 3600s.")

        try:
            # Fetch the specific Menu container (e.g., 'Main Menu')
            menu = Menu.objects.get(slug=menu_slug)
            
            # Fetch all MenuItem instances belonging to this menu.
            # MPTT already ensures they are correctly ordered for tree traversal implicitly.
            all_menu_items = list(menu.items.all()) # Evaluate to list to ensure direct access and caching

            # --- DYNAMIC SUB-MENU GENERATION LOGIC ---
            # Iterate through all menu items to check for dynamic content generation.
            # This attaches `dynamic_children` attribute to the `MenuItem` instances which
            # will be used by the recursive template.
            for item_obj in all_menu_items: 
                item_obj.dynamic_children = [] # Initialize dynamic_children for every item

                # Determine display limits for dynamic content from SiteConfiguration
                blog_cat_limit = getattr(site_config, 'blog_items_per_page', 9) if site_config else 9
                important_pages_limit = getattr(site_config, 'search_importance_limit', 3) if site_config else 3

                if item_obj.link_type == MenuItem.LinkType.ALL_BLOG_CATEGORIES:
                    # Fetch and process the entire category tree for the blog.
                    # Filters: only categories with published posts, ordered by post count.
                    blog_categories = Category.objects.annotate(
                        num_blog_posts=Count('blog_posts', filter=Q(blog_posts__status='published'))
                    ).filter(num_blog_posts__gt=0).order_by('tree_id', 'lft') # MPTT order for categories
                    
                    item_obj.dynamic_children = list(blog_categories[:blog_cat_limit]) 
                    logger.debug(f"Attached {len(item_obj.dynamic_children)} blog categories to menu item '{item_obj.title}'.")


                elif item_obj.link_type == MenuItem.LinkType.IMPORTANT_PAGES:
                    # Fetch and process important pages.
                    # Filters: published, importance_order below 99, ordered by importance.
                    important_pages_qs = Page.objects.filter(
                        status='published', 
                        importance_order__lt=99 
                    ).order_by('importance_order', 'title')[:important_pages_limit]
                    
                    item_obj.dynamic_children = list(important_pages_qs)
                    logger.debug(f"Attached {len(item_obj.dynamic_children)} important pages to menu item '{item_obj.title}'.")

            # Store the processed items (with dynamic_children attached) in cache.
            # Only cache if timeout is greater than 0.
            if timeout > 0: 
                cache.set(cache_key, all_menu_items, timeout)
            
            menu_items_processed = all_menu_items 

        except Menu.DoesNotExist:
            logger.warning(f"Menu with slug '{menu_slug}' does not exist. Cannot display menu.")
            menu_items_processed = [] # Return empty list if menu does not exist
        
    else:
        logger.debug(f"CACHE HIT for menu '{menu_slug}' (lang: {language_code}). Serving from cache.")
            
    # The 'nodes' variable is what the '_navbar_recursive.html' template expects.
    return {'nodes': menu_items_processed} 


# --- show_social_links_menu ---
@register.inclusion_tag('menus/partials/_social_links_partial.html', takes_context=True)
def show_social_links_menu(context):
    """
    Renders the social media links menu.
    It's a simplified version of show_menu for a fixed slug 'social-links'.
    """
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    cache_key = f'social_links_menu_{language_code}_v1'
    
    menu_items_processed = cache.get(cache_key)

    if menu_items_processed is None:
        logger.info(f"CACHE MISS for 'social-links' menu (lang: {language_code}). Querying database.")
        
        try:
            from site_settings.models import SiteConfiguration # Import here
            timeout = SiteConfiguration.objects.get().menu_cache_timeout
        except (ImportError, SiteConfiguration.DoesNotExist):
            timeout = 3600 # Fallback

        try:
            menu = Menu.objects.get(slug='social-links')
            menu_items_processed = list(menu.items.all()) # Simple list of items for social links

            if timeout > 0:
                cache.set(cache_key, menu_items_processed, timeout)

        except Menu.DoesNotExist:
            logger.warning("Menu with slug 'social-links' does not exist. Cannot display social media icons.")
            menu_items_processed = []
    else:
        logger.debug(f"CACHE HIT for 'social-links' menu (lang: {language_code}). Serving from cache.")

    return {'nodes': menu_items_processed}