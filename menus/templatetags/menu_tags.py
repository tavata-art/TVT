# File: menus/templatetags/menu_tags.py
import logging
from django import template
from django.core.cache import cache
from django.conf import settings

# Import all models needed for the dynamic logic
from ..models import Menu
from pages.models import Page
from categories.models import Category
from site_settings.models import SiteConfiguration

logger = logging.getLogger(__name__)
register = template.Library()

@register.inclusion_tag('core/partials/_tree_node_component.html')
def render_menu_tree(menu_slug):
    try:
        menu = Menu.objects.get(slug=menu_slug)
        nodes = menu.items.all() # Pasamos todos los items
        return {'nodes': nodes}
    except Menu.DoesNotExist:
        return {'nodes': []}

@register.inclusion_tag('menus/partials/_navbar_recursive.html', takes_context=True)
def show_menu(context, menu_slug):
    """
    Fetches and renders a full menu tree by its slug.
    It handles caching and dynamically generating sub-items for special menu item types.
    """
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    cache_key = f'menu_nodes_{menu_slug}_{language_code}_v1'
    
    # 1. Try to get the fully processed menu tree from cache
    nodes = cache.get(cache_key)

    if nodes is None:
        logger.info(f"CACHE MISS for menu '{menu_slug}' (lang: {language_code}). Building menu tree.")
        try:
            menu = Menu.objects.get(slug=menu_slug)
            # Get the top-level menu items. MPTT handles the tree structure.
            # We use prefetch_related for a small performance boost.
            nodes = menu.items.filter(parent__isnull=True).prefetch_related('children')
            
            # --- DYNAMIC SUB-MENU GENERATION LOGIC ---
            for node in nodes:
                if node.link_type == 'all_blog_categories':
                    # If it's a category tree item, fetch the category tree
                    node.dynamic_children = Category.objects.filter(parent__isnull=True)
                elif node.link_type == 'important_pages':
                    # If it's an important pages item, fetch those pages
                    config = SiteConfiguration.objects.get()
                    node.dynamic_children = Page.objects.filter(
                        status='published', 
                        importance_order__lt=99
                    ).order_by('importance_order')[:config.search_importance_limit]
            
            # Get cache timeout from settings
            timeout = SiteConfiguration.objects.get().menu_cache_timeout
            cache.set(cache_key, list(nodes), timeout)

        except Menu.DoesNotExist:
            logger.warning(f"Menu with slug '{menu_slug}' does not exist.")
            nodes = []
    else:
        logger.debug(f"CACHE HIT for menu '{menu_slug}' (lang: {language_code}). Serving from cache.")
            
    return {'nodes': nodes}

@register.inclusion_tag('menus/partials/_navbar_recursive.html', takes_context=True)
def render_navbar_menu(context, menu_slug):
    """
    Fetches and prepares the menu tree specifically for Bootstrap navbar rendering.
    """
    # La lógica de caché y de obtención de datos es la misma
    language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
    cache_key = f'navbar_nodes_{menu_slug}_{language_code}_v1'

    nodes = cache.get(cache_key)

    if nodes is None:
        logger.info(f"CACHE MISS for navbar menu '{menu_slug}' (lang: {language_code}).")
        try:
            menu = Menu.objects.get(slug=menu_slug)
            # Obtenemos solo los nodos raíz, la plantilla hará la recursión
            nodes = menu.items.filter(parent__isnull=True)

            timeout = SiteConfiguration.objects.get().menu_cache_timeout
            cache.set(cache_key, list(nodes), timeout)

        except Menu.DoesNotExist:
            nodes = []
    else:
        logger.debug(f"CACHE HIT for navbar menu '{menu_slug}' (lang: {language_code}).")

    return {'nodes': nodes, 'request': context['request']}

# The show_social_links tag can be kept as it is, as its logic is simple
# or refactored into the main show_menu if desired. We'll keep it separate for clarity.
@register.inclusion_tag('menus/social_links_menu.html')
def show_social_links():
    """ Renders the dedicated social media links menu. """
    # ... (la lógica de caché y consulta para 'social-links' se mantiene igual)

    cache_key = 'social_links_menu_v1'
    menu_items = cache.get(cache_key)

    if menu_items is None:
        # ... logic to fetch menu items for slug 'social-links' ...
        pass # Placeholder for your existing logic
    
    return {'menu_items': menu_items}
