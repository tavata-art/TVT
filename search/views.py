# search/views.py
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from pages.models import Page
from blog.models import Post

def search_results_view(request):
    """
    Performs a search across Pages and Blog Posts and paginates the results.
    """
    query = request.GET.get('q', '') # Use '' as a default to avoid None

    # Initialize empty QuerySets as a starting point
    all_page_results = Page.objects.none()
    all_post_results = Post.objects.none()
    
    # Only perform the search if a query was submitted
    if query:
        page_query = Q(title__icontains=query) | Q(content__icontains=query)
        all_page_results = Page.objects.filter(page_query, status='published').distinct()
        
        post_query = Q(title__icontains=query) | Q(content__icontains=query)
        all_post_results = Post.objects.filter(post_query, status='published').distinct().order_by('-published_date')

    # --- Paginate Page Results ---
    page_paginator = Paginator(all_page_results, 5) # Show 5 pages per results page
    page_page_number = request.GET.get('page_page') # Use a unique param name
    try:
        paginated_page_results = page_paginator.page(page_page_number)
    except (PageNotAnInteger, EmptyPage):
        paginated_page_results = page_paginator.page(1)
    
    # --- Paginate Post Results ---
    post_paginator = Paginator(all_post_results, 5) # Show 5 posts per results page
    post_page_number = request.GET.get('post_page') # Use another unique param name
    try:
        paginated_post_results = post_paginator.page(post_page_number)
    except (PageNotAnInteger, EmptyPage):
        paginated_post_results = post_paginator.page(1)
    
    # Calculate total results based on the original full querysets
    total_results = all_page_results.count() + all_post_results.count()

    context = {
        'query': query,
        'page_results': paginated_page_results,
        'post_results': paginated_post_results,
        'total_results': total_results,
    }

    return render(request, 'search/search_results.html', context)