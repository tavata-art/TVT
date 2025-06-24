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

logger = logging.getLogger(__name__)

# Import SiteConfiguration for cache timeout settings (handle potential ImportError or DoesNotExist)
try:
    from site_settings.models import SiteConfiguration
except ImportError:
    logger.error("Could not import SiteConfiguration. Ensure 'site_settings' app is in INSTALLED_APPS.")
    SiteConfiguration = None # Fallback for type hinting / future handling

logger = logging.getLogger(__name__) # Get logger specific to this module
register = template.Library() # Register this as a Django template library


@register.inclusion_tag('menus/partials/_navbar_main_level.html', takes_context=True)
def show_menu(context, menu_slug):
    """
    Fetches and renders the top-level menu items for a main navigation bar.
    Handles caching and prepares dynamic sub-items.
    """
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    cache_key = f'menu_nodes_main_level_{menu_slug}_{language_code}_v1'
    
    # Try getting the top-level nodes (with attached dynamic_children) from cache
    top_level_nodes = cache.get(cache_key)

    if top_level_nodes is None:
        logger.info(f"CACHE MISS for main level menu '{menu_slug}' (lang: {language_code}). Building.")
        try:
            menu = Menu.objects.get(slug=menu_slug)
            
            # Fetch ALL menu items for this menu. 
            # We need them all to attach dynamic children to parents properly.
            all_menu_items = list(menu.items.all().order_by('tree_id', 'lft'))
            
            # --- ATTACH DYNAMIC CHILDREN LOGIC ---
            # This loop attaches 'dynamic_children' to the relevant parent MenuItem instances,
            # which will be used by the template during rendering.
            for item_obj in all_menu_items: 
                item_obj.dynamic_children = [] # Initialize for all items

                blog_cat_limit = getattr(SiteConfiguration.get_solo(), 'blog_items_per_page', 9) if SiteConfiguration else 9
                important_pages_limit = getattr(SiteConfiguration.get_solo(), 'search_importance_limit', 3) if SiteConfiguration else 3

                if item_obj.link_type == MenuItem.LinkType.ALL_BLOG_CATEGORIES:
                    blog_categories = Category.objects.annotate(
                        num_blog_posts=Count('blog_posts', filter=Q(blog_posts__status='published'))
                    ).filter(num_blog_posts__gt=0).order_by('tree_id', 'lft')
                    item_obj.dynamic_children = list(blog_categories[:blog_cat_limit])

                elif item_obj.link_type == MenuItem.LinkType.IMPORTANT_PAGES:
                    important_pages_qs = Page.objects.filter(
                        status='published', 
                        importance_order__lt=99
                    ).order_by('importance_order', 'title')
                    item_obj.dynamic_children = list(important_pages_qs[:important_pages_limit])

            # Now, filter for only the top-level nodes (level 0) for the main navbar.
            # The children will be accessed in the template using .children.all() and .dynamic_children
            # on these top-level nodes.
            raw_top_level_nodes = [item for item in all_menu_items if item.level == 0]

            # Get cache timeout and set cache.
            try:
                config = SiteConfiguration.get_solo()
                timeout = config.menu_cache_timeout
            except SiteConfiguration.DoesNotExist:
                timeout = 3600
            
            cache.set(cache_key, raw_top_level_nodes, timeout) # Cache only top-level nodes for efficiency
            top_level_nodes = raw_top_level_nodes
            
        except Menu.DoesNotExist:
            logger.warning(f"Menu with slug '{menu_slug}' does not exist.")
            top_level_nodes = [] # Return empty list if menu does not exist
    else:
        logger.debug(f"CACHE HIT for main level menu '{menu_slug}' (lang: {language_code}). Serving from cache.")
            
    return {'nodes': top_level_nodes} # Pass only top-level nodes to _navbar_main_level.html



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
            timeout = SiteConfiguration.get_solo().menu_cache_timeout
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

@register.inclusion_tag('menus/partials/_simple_horizontal_menu.html', takes_context=True)
def show_simple_menu(context, menu_slug):
    """
    Fetches and renders menu items for a simple, non-hierarchical menu
    like a footer menu.
    """
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    cache_key = f'simple_menu_items_{menu_slug}_{language_code}_v1'
    
    items = cache.get(cache_key)

    if items is None:
        logger.info(f"CACHE MISS for simple menu '{menu_slug}' (lang: {language_code}). Building.")
        try:
            menu = Menu.objects.get(slug=menu_slug)
            # Solo queremos los items de nivel 0, ya que es un menú simple.
            items = list(menu.items.filter(level=0).order_by('order')) 
            
            try:
                config = SiteConfiguration.objects.get()
                timeout = config.menu_cache_timeout
            except SiteConfiguration.DoesNotExist:
                timeout = 3600
            
            cache.set(cache_key, items, timeout)
            
        except Menu.DoesNotExist:
            logger.warning(f"Menu with slug '{menu_slug}' does not exist for show_simple_menu.")
            items = []
    else:
        logger.debug(f"CACHE HIT for simple menu '{menu_slug}' (lang: {language_code}).")

    return {'nodes': items}