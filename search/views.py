# search/views.py
from django.shortcuts import render
from django.db.models import Q
from pages.models import Page
from blog.models import Post

def search_results_view(request):
    """
    Performs a search across Pages and Blog Posts based on the query parameter.
    """
    # Get the search term from the URL's 'q' parameter.
    query = request.GET.get('q')

    page_results = []
    post_results = []

    # Only perform the search if a query was submitted.
    if query:
        # The Q object allows for complex queries, like using OR (|).
        # __icontains makes the search case-insensitive.
        page_query = Q(title__icontains=query) | Q(content__icontains=query)
        # We also filter to only show published pages.
        page_results = Page.objects.filter(page_query, status='published').distinct()

        post_query = Q(title__icontains=query) | Q(content__icontains=query)
        # And only published blog posts.
        post_results = Post.objects.filter(post_query, status='published').distinct()
        total_results = page_results.count() + post_results.count()

        context = {
            'query': query,
            'page_results': page_results,
            'post_results': post_results,
            'total_results': total_results, 
        }
        return render(request, 'search/search_results.html', context)
