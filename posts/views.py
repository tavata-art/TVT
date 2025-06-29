# File: posts/views.py

from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils.translation import get_language

def post_list_view(request):
    """
    🔍 Lists all published posts (basic view).
    """
    posts = Post.objects.filter(status='published').order_by('-published_date')
    return render(request, 'posts/post_list.html', {'posts': posts})


import logging
from django.shortcuts import render
from django.utils.translation import get_language, gettext_lazy as _
from django.http import Http404
from .models import Post

logger = logging.getLogger(__name__)

def post_detail_view(request, year, month, day, slug):
    """
    🧠 View to retrieve and render a single Post in the correct language using django-parler.
    Supports multilingual slugs and provides precise logging.
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

    return render(request, 'posts/post_detail.html', {
        "post": post
    })
