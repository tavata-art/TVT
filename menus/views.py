# File: menus/views.py
from django.shortcuts import render
from .models import Menu

def menu_test_view(request):
    """
    A dedicated view to test and debug the rendering of the main menu tree.
    """
    try:
        # We fetch the top-level items of the 'main-menu'.
        menu = Menu.objects.get(slug='main-menu')
        root_nodes = menu.items.filter(parent__isnull=True)
    except Menu.DoesNotExist:
        root_nodes = []

    return render(request, 'menus/menu_page.html', {'nodes': root_nodes})
