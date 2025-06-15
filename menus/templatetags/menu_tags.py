# menus/templatetags/menu_tags.py
from django import template
from menus.models import MenuItem

register = template.Library()

@register.inclusion_tag('menus/main_menu.html')
def show_main_menu():
    """
    Renderiza el menú de navegación principal.
    """
    menu_items = MenuItem.objects.all()
    return {'menu_items': menu_items}