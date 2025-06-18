# menus/templatetags/menu_tags.py
import logging
from django import template
from ..models import Menu # Importamos desde el mismo nivel de la app

logger = logging.getLogger(__name__)
register = template.Library()

@register.inclusion_tag('menus/render_menu.html')
def show_menu(menu_slug):
    """
    Renderiza un menú específico basado en su slug.
    """
    try:
        # prefetch_related es una optimización CLAVE para evitar múltiples consultas a la BD
        menu = Menu.objects.prefetch_related('items').get(slug=menu_slug)
        return {'menu_items': menu.items.all()}
    except Menu.DoesNotExist:
        # Si el menú no existe, registramos un aviso y devolvemos una lista vacía
        logger.warning(f"Menu with slug '{menu_slug}' not found in database.")
        # Si el menú no existe, devolvemos una lista vacía para no romper la plantilla
        return {'menu_items': []}
    
@register.inclusion_tag('menus/social_links_menu.html')
def show_social_links():
    try:
        menu = Menu.objects.get(slug='social-links')
        return {'menu_items': menu.items.all()}
    except Menu.DoesNotExist:
        return {'menu_items': []}