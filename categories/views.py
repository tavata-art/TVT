# File: categories/views.py
from django.shortcuts import render
from .models import Category
from blog.models import Post
from django.urls import reverse
from django.utils.translation import gettext
from django.shortcuts import get_object_or_404

def category_tree_view(request):
    """
    Provides the root nodes for rendering a full category tree.
    """
    # We fetch ONLY the top-level categories.
    root_nodes = Category.objects.filter(parent__isnull=True)

    breadcrumbs = [
        {"url": "/", "label": gettext("Home")},
        {"url": "", "label": gettext("Categories")},
    ]

    context = {
        'categories': root_nodes,
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'categories/category_tree.html', context)

def build_category_breadcrumbs(category):
    path = []
    current = category
    while current:
        path.append({
            "url": reverse("blog:posts_by_category", args=[current.slug]),
            "label": current.name,
        })
        current = current.parent
    return reversed(path)

def posts_by_category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    posts = Post.objects.filter(categories=category, is_published=True).order_by('-publish')

    breadcrumbs = [
        {"url": "/", "label": gettext("Home")},
        {"url": reverse("blog:post_list"), "label": gettext("Blog")},
    ]
    breadcrumbs += list(build_category_breadcrumbs(category))

    return render(request, "blog/posts_by_category.html", {
        "category": category,
        "posts": posts,
        "breadcrumbs": breadcrumbs,
    })