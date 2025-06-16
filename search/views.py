# search/views.py
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from pages.models import Page
from blog.models import Post

# ¡NUEVO IMPORT! Importamos nuestro modelo de configuración.
from site_settings.models import SiteConfiguration

def search_results_view(request):
    """
    Performs a search and paginates the results for both Pages and Posts,
    using settings from the SiteConfiguration model.
    """
    # 1. Get the site-wide configuration settings first.
    #    .get() is safe here because django-solo guarantees only one object.
    site_config = SiteConfiguration.objects.get()
    
    query = request.GET.get('q', '')
    
    all_page_results = Page.objects.none()
    all_post_results = Post.objects.none()
    
    if query:
        # Get all matching objects first
        page_query = Q(title__icontains=query) | Q(content__icontains=query)
        all_page_results = Page.objects.filter(page_query, status='published').distinct()
        
        post_query = Q(title__icontains=query) | Q(content__icontains=query)
        all_post_results = Post.objects.filter(post_query, status='published').distinct().order_by('-published_date')

    # --- Paginate Page Results using the dynamic setting ---
    page_paginator = Paginator(all_page_results, site_config.search_results_per_page) # <-- USAMOS EL VALOR DINÁMICO
    page_page_number = request.GET.get('page_page')
    try:
        paginated_page_results = page_paginator.page(page_page_number)
    except (PageNotAnInteger, EmptyPage):
        paginated_page_results = page_paginator.page(1)
    
    # --- Paginate Post Results using the SAME dynamic setting ---
    post_paginator = Paginator(all_post_results, site_config.search_results_per_page) # <-- USAMOS EL VALOR DINÁMICO
    post_page_number = request.GET.get('post_page')
    try:
        paginated_post_results = post_paginator.page(post_page_number)
    except (PageNotAnInteger, EmptyPage):
        paginated_post_results = post_paginator.page(1)
    
    # Calculate total results
    total_results = all_page_results.count() + all_post_results.count()

    context = {
        'query': query,
        'page_results': paginated_page_results,
        'post_results': paginated_post_results,
        'total_results': total_results,
    }

    return render(request, 'search/search_results.html', context)