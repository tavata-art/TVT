# File: menus/views.py
from django.shortcuts import render
from .models import Menu

def menu_view(request):
    # La plantilla ahora se encargará de llamar al tag
    return render(request, 'menus/menu_page.html')
