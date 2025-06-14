# pages/views.py
from django.shortcuts import render, get_object_or_404
from .models import Page, Category

def page_detail_view(request, slug):
    # Buscamos una página que coincida con el slug Y que esté publicada.
    # Si no la encuentra, automáticamente devuelve un error 404.
    page = get_object_or_404(Page, slug=slug, status='published')

    # El contexto es el diccionario de datos que pasamos a la plantilla.
    context = {
        'page': page
    }

    return render(request, 'pages/page_detail.html', context)

# --- NUEVA VISTA ---
def pages_by_category_view(request, category_slug):
    """
    Recupera y muestra todas las páginas publicadas que pertenecen
    a una categoría específica.
    """
    # 1. Obtener el objeto de la categoría. Si no existe, devuelve un error 404.
    category = get_object_or_404(Category, slug=category_slug)

    # 2. Filtrar las páginas. Usamos el 'related_name="pages"' que definimos en el modelo.
    #    Solo queremos las páginas que estén 'published'.
    pages_in_category = category.pages.filter(status='published')

    # 3. Preparar el contexto para la plantilla.
    context = {
        'category': category,
        'pages_list': pages_in_category, # Usamos un nombre de variable claro
    }

    # 4. Renderizar la plantilla, pasándole el contexto.
    return render(request, 'pages/pages_by_category.html', context)