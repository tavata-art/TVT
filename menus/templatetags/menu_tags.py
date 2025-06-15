# menus/templatetags/menu_tags.py
from django import template
from ..models import Menu # Importamos desde el mismo nivel de la app

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
        # Si el menú no existe, devolvemos una lista vacía para no romper la plantilla
        return {'menu_items': []}