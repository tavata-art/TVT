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
from categories.models import Category
from comments.models import Comment
from comments.forms import CommentForm
from tags.models import Tag
from site_settings.models import SiteConfiguration
from django.conf import settings
from django.db.models import Q

logger = logging.getLogger(__name__)

def post_list_view(request):
    """
    📚 Lists all published posts with pagination and breadcrumbs.
    """
    # 1. Get all published posts
    all_posts = Post.objects.filter(status='published').order_by('-published_date')

    # 2. Determine posts per page
    try:
        config = SiteConfiguration.get_solo()
        posts_per_page = config.blog_items_per_page
    except SiteConfiguration.DoesNotExist:
        posts_per_page = 6
        logger.warning("⚠️ SiteConfiguration missing. Using default of 6 posts per page.")

    # 3. Paginate
    paginator = Paginator(all_posts, posts_per_page)
    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        logger.info("📄 Page number is not an integer. Delivering first page.")
        posts = paginator.page(1)
    except EmptyPage:
        logger.info("📄 Page out of range. Delivering last page.")
        posts = paginator.page(paginator.num_pages)

    # 4. Context with breadcrumbs
    breadcrumbs = [
        {"url": "/", "label": _("Home")},
        {"url": "", "label": _("Posts")},
    ]

    return render(request, 'posts/post_list.html', {
        "posts": posts,
        "breadcrumbs": breadcrumbs
    })

def get_category_depth(category):
    depth = 0
    current = category
    while current.parent:
        depth += 1
        current = current.parent
    return depth

def get_fallback(instance, field_name, language):
    val = getattr(instance, f"{field_name}_{language}", None)
    if val:
        return val
    return getattr(instance, f"{field_name}_{settings.LANGUAGE_CODE}", f"[{field_name}]")

def build_category_breadcrumbs(category):
    path = []
    current = category
    lang = get_language()

    while current:
        path.append({
            "url": reverse("posts:posts_by_category", args=[get_fallback(current, "slug", lang)]),
            "label": get_fallback(current, "name", lang),
        })
        current = current.parent
    return reversed(path)

def post_detail_view(request, year, month, day, slug):
    """
    🌐 Displays a single multilingual post, handles view count increment,
    comment submission, and breadcrumb generation including categories.
    """
    language = get_language()
    logger.debug(f"🌐 Language: {language} | Slug: {slug} | 📅 {year}-{month}-{day}")

    # 1. Retrieve post in current language
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

    # 3. Retrieve site config for comment approval
    try:
        config = SiteConfiguration.get_solo()
    except SiteConfiguration.DoesNotExist:
        logger.warning("⚠️ SiteConfiguration not found. Fallback approval=False.")
        class ConfigFallback: auto_approve_comments = False
        config = ConfigFallback()

    # 4. Handle approved comments
    comments = Comment.objects.filter(post=post, is_approved=True)

    # 5. Handle new comment submission
    if request.method == 'POST':
        comment_form = CommentForm(request.POST, user=request.user)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post

            if request.user.is_authenticated:
                profile = getattr(request.user, 'profile', None)
                new_comment.user = request.user
                new_comment.author_name = profile.get_display_name() if profile else request.user.username
                new_comment.author_email = request.user.email
                is_trusted = getattr(profile, 'is_trusted_commenter', False)
            else:
                is_trusted = False

            new_comment.is_approved = config.auto_approve_comments or is_trusted
            new_comment.save()

            msg = gettext("✅ Thank you! Your comment has been published.") if new_comment.is_approved \
                else gettext("🕓 Thank you! Your comment awaits moderation.")
            messages.success(request, msg)

            return HttpResponseRedirect(f"{post.get_absolute_url()}#comments-section")
        else:
            logger.warning(f"❌ Invalid comment submission: {comment_form.errors.as_json()}")
    else:
        comment_form = CommentForm(user=request.user)

    # 6. Breadcrumbs with optional category
    categories = list(post.categories.all())
    category = None
    if categories:
        categories.sort(key=lambda c: (get_category_depth(c), c.id))
        category = categories[0]

    breadcrumbs = [
        {'url': '/', 'label': gettext("Home")},
        {'url': reverse("posts:post_list"), 'label': gettext("Posts")},
    ]
    if category:
        breadcrumbs += list(build_category_breadcrumbs(category))
    breadcrumbs.append({'url': '', 'label': post.safe_translation_getter("title", any_language=True)})

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'breadcrumbs': breadcrumbs,
        'translatable_object': post,
    })

def posts_by_category_view(request, category_slug):
    """
    📂 View para listar los posts publicados de una categoría específica.
    Compatible con jerarquía, traducción y paginación.
    """
    language = get_language()

    # 🧭 Buscar la categoría multilingüe por el slug del idioma actual
    lookup = Q()
    for lang_code, _ in settings.LANGUAGES:
        lookup |= Q(**{f"slug_{lang_code}": category_slug})

    category = get_object_or_404(Category, lookup)
    all_posts = Post.objects.filter(status='published', categories=category).order_by('-published_date')

    try:
        config = SiteConfiguration.get_solo()
        posts_per_page = config.blog_items_per_page
    except SiteConfiguration.DoesNotExist:
        posts_per_page = 6
        logger.warning("⚠️ SiteConfiguration no encontrada. Usando paginación por defecto.")

    paginator = Paginator(all_posts, posts_per_page)
    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    fallback_posts = Post.objects.language(language).filter(status='published') \
                      .exclude(pk__in=[p.pk for p in posts]) \
                      .order_by('-published_date')[:3]
    
    breadcrumbs = [
        {"url": "/", "label": gettext("Home")},
        {"url": reverse("posts:post_list"), "label": gettext("Posts")},
    ] + list(build_category_breadcrumbs(category))

    context = {
        "category": category,
        "posts": posts,
        "breadcrumbs": breadcrumbs,
        'fallback_posts': fallback_posts,
    }
    return render(request, "posts/posts_by_category.html", context)

def posts_by_tag_view(request, tag_slug):
    """
    🏷️ View to list all posts associated with a given tag, with pagination and fallback suggestions.
    """
    language = get_language()
    tag = get_object_or_404(Tag, slug=tag_slug)

    # Posts that have the selected tag
    all_tagged_posts = Post.objects.language(language).filter(
        tags=tag,
        status='published'
    ).order_by('-published_date')

    # Pagination config
    try:
        from site_settings.models import SiteConfiguration
        config = SiteConfiguration.get_solo()
        per_page = config.blog_items_per_page
    except Exception:
        per_page = 6  # Default fallback

    paginator = Paginator(all_tagged_posts, per_page)
    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Fallback: show other recent posts if none found in this tag
    fallback_posts = Post.objects.language(language).filter(status='published') \
        .exclude(pk__in=[p.pk for p in posts]) \
        .order_by('-published_date')[:3]

    context = {
        'tag': tag,
        'posts': posts,
        'fallback_posts': fallback_posts,
        'tag_label': tag.safe_translation_getter("label", any_language=True),
        'breadcrumbs': [
            {"url": "/", "label": gettext("Home")},
            {"url": "/posts/", "label": gettext("Posts")},
            {"url": "", "label": tag.safe_translation_getter("label", any_language=True)},
        ],
    }

    return render(request, 'posts/posts_by_tag.html', context)