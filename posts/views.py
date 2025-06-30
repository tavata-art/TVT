# File: posts/views.py

import logging
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _, gettext, get_language
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.contrib import messages

from .models import Post
from comments.models import Comment
from comments.forms import CommentForm
from tags.models import Tag
from site_settings.models import SiteConfiguration

logger = logging.getLogger(__name__)

def post_list_view(request):
    """📚 View to list all published posts."""
    posts = Post.objects.filter(status='published').order_by('-published_date')

    # Pagination (optional future)
    context = {
        'posts': posts,
        'breadcrumbs': [
            {'url': '/', 'label': gettext("Home")},
            {'url': '', 'label': gettext("Posts")},
        ]
    }
    return render(request, 'posts/post_list.html', context)

def post_detail_view(request, year, month, day, slug):
    """🧠 View to display a single post with comments and form submission logic."""
    language = get_language()
    logger.debug(f"🌐 Language: {language} | Slug: {slug} | 📅 {year}-{month}-{day}")

    # 1. Fetch post in current language
    post = get_object_or_404(
        Post.objects.language(language),
        translations__slug=slug,
        published_date__year=year,
        published_date__month=month,
        published_date__day=day,
        status='published'
    )

    # 2. Increment view count
    Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    post.refresh_from_db()

    # 3. Site configuration (for auto-approval)
    try:
        config = SiteConfiguration.get_solo()
    except SiteConfiguration.DoesNotExist:
        logger.warning("⚠️ SiteConfiguration not found. Using default approval = False.")
        class ConfigFallback:
            auto_approve_comments = False
        config = ConfigFallback()

    # 4. Handle comment submission
    comments = Comment.objects.filter(post=post, is_approved=True)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, user=request.user)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post

            if request.user.is_authenticated:
                new_comment.user = request.user
                new_comment.author_name = request.user.profile.get_display_name()
                new_comment.author_email = request.user.email
                is_trusted = getattr(request.user.profile, 'is_trusted_commenter', False)
            else:
                is_trusted = False

            # Approval logic
            if config.auto_approve_comments or is_trusted:
                new_comment.is_approved = True
                messages.success(request, gettext("✅ Thank you! Your comment has been published."))
            else:
                new_comment.is_approved = False
                messages.info(request, gettext("🕓 Thank you! Your comment awaits moderation."))

            new_comment.save()
            return HttpResponseRedirect(f"{post.get_absolute_url()}#comments-section")
        else:
            logger.warning(f"❌ Invalid comment form: {comment_form.errors.as_json()}")
    else:
        comment_form = CommentForm(user=request.user)

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'breadcrumbs': [
            {'url': '/', 'label': gettext("Home")},
            {'url': reverse("posts:post_list"), 'label': gettext("Posts")},
            {'url': '', 'label': post.safe_translation_getter("title", any_language=True)},
        ]
    }
    return render(request, 'posts/post_detail.html', context)

def posts_by_tag_view(request, tag_slug):
    """
    🏷️ View to list all posts associated with a given tag.
    """
    language = get_language()
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.language(language).filter(tags=tag, status='published').order_by('-published_date')
    logger.info(f"📌 Showing posts for tag: {tag.safe_translation_getter('label', any_language=True)} [{language}]")
    
    context = {
        'tag': tag,
        'posts': posts,
        'breadcrumbs': [
            {"url": "/", "label": gettext("Home")},
            {"url": reverse("posts:post_list"), "label": gettext("Posts")},
            {"url": "", "label": tag.safe_translation_getter("label", any_language=True)},
        ],
        "tag_label": tag.safe_translation_getter("label", any_language=True) 
    }
    return render(request, 'posts/posts_by_tag.html', context)
