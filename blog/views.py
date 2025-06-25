import logging
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext
from django.urls import reverse

from .forms import CommentForm
from .models import Post, Comment
from categories.models import Category
from site_settings.models import SiteConfiguration
from taggit.models import Tag

logger = logging.getLogger(__name__)

def posts_by_tag_view(request, tag_slug):
    """
    Displays a paginated list of published posts associated with a specific tag.
    """
    # 1. Get the Tag object by slug, or return a 404
    tag = get_object_or_404(Tag, slug=tag_slug)

    # 2. Get all published posts associated with this tag
    all_posts_by_tag = Post.objects.filter(
        status='published', tags__slug=tag_slug
    ).order_by('-published_date')

    # 3. Get pagination settings
    try:
        site_config = SiteConfiguration.get_solo()
        posts_per_page = site_config.blog_items_per_page
    except SiteConfiguration.DoesNotExist:
        posts_per_page = 6
        logger.warning("SiteConfiguration not found. Using default tag pagination.")

    # 4. Apply pagination
    paginator = Paginator(all_posts_by_tag, posts_per_page)
    page_number = request.GET.get('page')

    try:
        posts = paginator.get_page(page_number)
    except PageNotAnInteger:
        posts = paginator.get_page(1)
    except EmptyPage:
        if paginator.num_pages > 0:
            posts = paginator.get_page(paginator.num_pages)
        else:
            posts = []

    logger.info(f"Posts by tag view accessed for tag '{tag_slug}'. Showing page {getattr(posts, 'number', 0)} of {getattr(posts, 'paginator.num_pages', 0)} posts.")

    context = {
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'blog/post_list_by_tag.html', context)

def post_list_view(request):
    """
    Displays a list of published blog posts, paginated.
    """
    # 1. Retrieve the full, ordered list of all published posts.
    all_posts = Post.objects.filter(status='published').order_by('-published_date')

    # 2. Create a Paginator instance.
    #    We'll show 6 posts per page. This number can be changed easily.
    try:
        config = SiteConfiguration.get_solo()
        posts_per_page = config.blog_items_per_page
    except SiteConfiguration.DoesNotExist:
        logger.warning(
                "SiteConfiguration does not exist. Using default indentation."
            )
        posts_per_page = 6  # Fallback
    paginator = Paginator(all_posts, posts_per_page)

    # 3. Get the page number from the URL's GET parameters (e.g., /blog/?page=2).
    page_number = request.GET.get('page')

    # 4. Get the specific Page object for the requested page number.
    #    This includes robust error handling.
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        logger.info(
                "If the 'page' parameter is not an integer, deliver the first page."
            )
        posts = paginator.page(1)
    except EmptyPage:
        logger.isEnabledFor(
                "If the page number is out of range (e.g., 999), deliver the last page."
            )
        posts = paginator.page(paginator.num_pages)

    # 5. Prepare the context to be passed to the template.
    #    The 'posts' variable is now a Paginator's Page object, not a simple list.
    breadcrumbs = [
        {"url": "/", "label": gettext("Home")},
        {"url": "", "label": gettext("Blog")},
    ]
    context = {
        'posts': posts,
        "breadcrumbs": breadcrumbs,
    }

    # 6. Render the template with the provided context.
    return render(request, 'blog/post_list.html', context)

def get_category_depth(category):
    depth = 0
    current = category
    while current.parent:
        depth += 1
        current = current.parent
    return depth

def build_category_breadcrumbs(category):
    """Devuelve una lista de dicts desde la raíz hasta la categoría"""
    path = []
    current = category
    while current:
        path.append({
            "url": reverse("blog:posts_by_category", args=[current.slug]),
            "label": current.name,
        })
        current = current.parent
    return reversed(path)  # children to father

def post_detail_view(request, year, month, day, slug):
    """
    Displays a single blog post and handles the entire comment submission process,
    including view counting, smart comment approval, and user association.
    """
    # 1. Retrieve the Post and Site Configuration objects.
    # ----------------------------------------------------
    post = get_object_or_404(Post,
                             status='published',
                             published_date__year=year,
                             published_date__month=month,
                             published_date__day=day,
                             slug=slug)

    try:
        site_config = SiteConfiguration.get_solo()
    except SiteConfiguration.DoesNotExist:
        logger.error("CRITICAL: SiteConfiguration object not found. Site may not function correctly.")
        # Create a fallback object to prevent crashes.
        class FallbackConfig:
            auto_approve_comments = False
        site_config = FallbackConfig()

    # 2. Increment the View Count.
    # ---------------------------------
    post.views_count = F('views_count') + 1
    post.save(update_fields=['views_count'])
    post.refresh_from_db()

    # 3. Handle Comment Submission and Retrieval.
    # -------------------------------------------
    comments = post.comments.filter(is_approved=True)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, user=request.user)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            
            # --- Smart Approval Logic ---
            is_trusted = False
            if request.user.is_authenticated:
                new_comment.user = request.user
                new_comment.author_name = request.user.profile.get_display_name()
                new_comment.author_email = request.user.email
                # Check if the user has been promoted to 'Trusted'.
                is_trusted = request.user.profile.is_trusted_commenter
            
            # Approve the comment if global auto-approval is ON, OR if the specific user is trusted.
            if site_config.auto_approve_comments or is_trusted:
                new_comment.is_approved = True
                success_message = gettext("Thank you! Your comment has been published.")
                if is_trusted and not site_config.auto_approve_comments:
                    logger.info(f"Comment from trusted user '{request.user.username}' was auto-approved.")
            else:
                new_comment.is_approved = False
                success_message = gettext("Thank you! Your comment has been submitted and is awaiting moderation.")

            new_comment.save()
            messages.success(request, success_message)
            
            # Redirect using the Post/Redirect/Get pattern.
            post_url = post.get_absolute_url()
            redirect_url = f"{post_url}#comments-section"
            return HttpResponseRedirect(redirect_url)
        else:
            logger.warning(f"Invalid comment submission on post '{post.slug}'. Errors: {comment_form.errors.as_json()}")
    else:
        # For a GET request, create a blank form instance.
        comment_form = CommentForm(user=request.user)

    # 4. Prepare the final context for the template.
    # ----------------------------------------------------l
    categories = list(post.categories.all())
    if categories:
        # Ordenar por (profundidad en el árbol, fecha de creación)
        categories.sort(key=lambda c: (get_category_depth(c), c.id))
        category = categories[0]
    else:
        category = None

    breadcrumbs = [
        {"url": "/", "label": gettext("Home")},
        {"url": reverse("blog:post_list"), "label": gettext("Blog")},  # o "Noticias", según el nombre
    ]
    if category:
        breadcrumbs += list(build_category_breadcrumbs(category))

    breadcrumbs.append({"url": "", "label": post.title})
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        "breadcrumbs": breadcrumbs,
        'translatable_object': post,
    }
    return render(request, 'blog/post_detail.html', context)

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
    """
    Filters and displays a paginated list of published posts
    belonging to a specific blog category.
    """
    # --- 1. Get Base Data ---
    category = get_object_or_404(Category, slug=category_slug)
    all_posts_in_category = category.blog_posts.filter(status='published').order_by('-published_date')

    # --- 2. Get Pagination Settings ---
    try:
        config = SiteConfiguration.get_solo()
        posts_per_page = config.blog_items_per_page
    except SiteConfiguration.DoesNotExist:
        logger.warning(
            "SiteConfiguration does not exist. Using default pagination settings."
        )
        posts_per_page = 6  # Fallback

    # --- 3. Apply Pagination ---
    paginator = Paginator(all_posts_in_category, posts_per_page)
    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If the 'page' parameter is not an integer, deliver the first page.
        logger.info("Page number is not an integer, delivering the first page.")
        posts = paginator.page(1)
    except EmptyPage:
        # If the page number is out of range (e.g., 999), deliver the last page.
        logger.info("Page number is out of range, delivering the last page.")
        posts = paginator.page(paginator.num_pages)

    # --- 4. Prepare Context and Render ---
    breadcrumbs = [
        {"url": "/", "label": gettext("Home")},
        {"url": reverse("blog:post_list"), "label": gettext("Blog")},
    ]
    breadcrumbs += list(build_category_breadcrumbs(category))

    context = {
        'category': category,
        "breadcrumbs": breadcrumbs,
        'posts': posts,  # Pass the paginated 'posts' object
    }
    return render(request, 'blog/post_list_by_category.html', context)

