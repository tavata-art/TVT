# File: categories/views.py
from django.shortcuts import render
from .models import Category

def category_tree_view(request):
    """
    Provides the root nodes for rendering a full category tree.
    """
    # We fetch ONLY the top-level categories.
    root_nodes = Category.objects.filter(parent__isnull=True)

    context = {
        'categories': root_nodes,
    }
    return render(request, 'categories/category_tree.html', context)