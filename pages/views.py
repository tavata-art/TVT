# pages/views.py
from django.shortcuts import render, get_object_or_404
from .models import Page

def page_detail_view(request, slug):
    # Buscamos una página que coincida con el slug Y que esté publicada.
    # Si no la encuentra, automáticamente devuelve un error 404.
    page = get_object_or_404(Page, slug=slug, status='published')

    # El contexto es el diccionario de datos que pasamos a la plantilla.
    context = {
        'page': page
    }

    return render(request, 'pages/page_detail.html', context)