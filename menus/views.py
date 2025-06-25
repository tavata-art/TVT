from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from django.urls import reverse
from .models import Menu

def menu_view(request, slug):
    menu = get_object_or_404(Menu, slug=slug)
    root_items = menu.items.filter(parent__isnull=True)

    breadcrumbs = [
        {"url": "/", "label": _("Home")},
        {"url": "", "label": _("Menus")},
        {"url": "", "label": menu.title},
    ]

    return render(request, "menus/menu_page.html", {
        "menu": menu,
        "menu_items": root_items,
        "breadcrumbs": breadcrumbs,
    })