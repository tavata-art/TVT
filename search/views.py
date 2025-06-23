# search/views.py
import logging
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from pages.models import Page
from blog.models import Post
from site_settings.models import SiteConfiguration

logger = logging.getLogger(__name__)

def search_results_view(request):
    """
    Performs a search across Pages and Blog Posts, ordering Pages by importance,
    and paginates the results correctly.
    """
    try:
        site_config = SiteConfiguration.get_solo()
        pages_per_page = site_config.search_pages_per_page
        posts_per_page = site_config.search_posts_per_page
    except SiteConfiguration.DoesNotExist:
        logger.warning("SiteConfiguration does not exist. Using default pagination settings.")
        pages_per_page = 5
        posts_per_page = 5

    query = request.GET.get('q', '')
    
    # Initialize with empty QuerySets
    page_results_qs = Page.objects.none()
    post_results_qs = Post.objects.none()

    if query:
        # Build the Q objects for the search query
        page_query = Q(title__icontains=query) | Q(content__icontains=query)
        post_query = Q(title__icontains=query) | Q(content__icontains=query)

        # --- ¡LA LÓGICA CORRECTA! ---
        # 1. Obtenemos TODAS las páginas que coinciden con la búsqueda.
        # 2. LUEGO, las ordenamos por importancia y después por título.
        page_results_qs = Page.objects.filter(page_query, status='published') \
                                      .distinct() \
                                      .order_by('importance_order', 'title')
        
        post_results_qs = Post.objects.filter(post_query, status='published') \
                                      .distinct().order_by('-published_date')

    # --- Paginación (ahora sobre los QuerySets correctos) ---
    page_paginator = Paginator(page_results_qs, pages_per_page)
    page_page_number = request.GET.get('p_page', 1)
    paginated_page_results = page_paginator.get_page(page_page_number)
    
    post_paginator = Paginator(post_results_qs, posts_per_page)
    post_page_number = request.GET.get('p_post', 1)
    paginated_post_results = post_paginator.get_page(post_page_number)
    
    # --- Contexto ---
    total_results = page_results_qs.count() + post_results_qs.count()

    context = {
        'query': query,
        'page_results': paginated_page_results,
        'post_results': paginated_post_results,
        'total_results': total_results,
    }

    return render(request, 'search/search_results.html', context)