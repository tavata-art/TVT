# File: posts/views.py

import logging

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language, gettext_lazy as _

from .models import Post
from tags.models import Tag

logger = logging.getLogger(__name__)


def post_list_view(request):
    """
    📄 Lists all published posts in reverse chronological order.
    """
    posts = Post.objects.filter(status='published').order_by('-published_date')

    breadcrumbs = [
        {"url": "/", "label": _("Home")},
        {"url": "", "label": _("Posts")},
    ]

    return render(request, 'posts/post_list.html', {
        'posts': posts,
        "breadcrumbs": breadcrumbs,
    })


def post_detail_view(request, year, month, day, slug):
    """
    🔍 Detail view for a single post.
    Retrieves the translated post using `django-parler` based on language and slug.
    """
    language = get_language()
    logger.debug(f"🌐 Language: {language} | 📅 {year}-{month}-{day} | 🔗 Slug: {slug}")

    try:
        post = Post.objects.language(language).get(
            translations__slug=slug,
            published_date__year=year,
            published_date__month=month,
            published_date__day=day,
            status='published'
        )
        logger.info(f"✅ Post found: '{post.safe_translation_getter('title', any_language=True)}' [{language}]")
    except Post.DoesNotExist:
        logger.warning(f"🚫 Post not found: slug='{slug}', lang='{language}'")
        raise Http404(_("No Post matches the given query."))

    breadcrumbs = [
        {'url': '/', 'label': _('Home')},
        {'url': '/posts/', 'label': _('Posts')},
        {'url': '', 'label': post.safe_translation_getter("title", any_language=True)},
    ]

    return render(request, 'posts/post_detail.html', {
        "post": post,
        'breadcrumbs': breadcrumbs,
    })


def posts_by_tag_view(request, tag_slug):
    """
    🏷️ View to list all posts associated with a given tag.
    """
    language = get_language()
    tag = get_object_or_404(Tag, slug=tag_slug)

    posts = Post.objects.language(language).filter(tags=tag, status='published').order_by('-published_date')
    logger.info(f"📌 Showing posts for tag: {tag.safe_translation_getter('label', any_language=True)} [{language}]")

    breadcrumbs = [
        {'url': '/', 'label': _('Home')},
        {'url': '/posts/', 'label': _('Posts')},
        {'url': '', 'label': tag.safe_translation_getter("label", any_language=True)}
    ]

    return render(request, "posts/posts_by_tag.html", {
        "tag": tag,
        "posts": posts,
        "breadcrumbs": breadcrumbs,
        "tag_label": tag.safe_translation_getter("label", any_language=True) 
    })
