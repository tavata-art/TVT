# pages/views.py
import logging
from django.shortcuts import render, get_object_or_404
from .models import Page
from categories.models import Category
from django.core.paginator import Paginator # Asegúrate de importar Paginator
from site_settings.models import SiteConfiguration

logger = logging.getLogger(__name__)

def page_detail_view(request, slug):
    # Buscamos una página que coincida con el slug Y que esté publicada.
    # Si no la encuentra, automáticamente devuelve un error 404.
    page = get_object_or_404(Page, slug=slug, status='published')

    # El contexto es el diccionario de datos que pasamos a la plantilla.
    context = {
        'page': page
    }

    return render(request, 'pages/page_detail.html', context)

def pages_by_category_view(request, category_slug):
    """
    Displays a paginated list of published pages belonging
    to a specific category.
    """
    category = get_object_or_404(Category, slug=category_slug)
    all_pages_in_category = category.pages.filter(status='published').order_by('title')

    try:
        site_config = SiteConfiguration.objects.get()
        # Usamos el mismo setting que para el blog para mantener la consistencia
        items_per_page = site_config.blog_items_per_page 
    except SiteConfiguration.DoesNotExist:
        logger.warning("SiteConfiguration does not exist. Using default items per page.")
        items_per_page = 9 # Fallback

    paginator = Paginator(all_pages_in_category, items_per_page)
    page_number = request.GET.get('page', 1)

    pages_list = paginator.get_page(page_number)

    context = {
        'category': category,
        'pages_list': pages_list, # Pasamos el objeto paginado
    }
    return render(request, 'pages/pages_by_category.html', context)
   