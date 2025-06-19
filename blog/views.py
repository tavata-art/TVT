import logging
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext

from .forms import CommentForm
from .models import Post, PostCategory, Comment
from site_settings.models import SiteConfiguration

logger = logging.getLogger(__name__)

def post_list_view(request):
    """
    Displays a list of published blog posts, paginated.
    """
    # 1. Retrieve the full, ordered list of all published posts.
    all_posts = Post.objects.filter(status='published').order_by('-published_date')

    # 2. Create a Paginator instance.
    #    We'll show 6 posts per page. This number can be changed easily.
    try:
        config = SiteConfiguration.objects.get()
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
    context = {
        'posts': posts,
    }

    # 6. Render the template with the provided context.
    return render(request, 'blog/post_list.html', context)

def post_detail_view(request, year, month, day, slug):
    """
    Displays a single blog post and handles the entire comment submission process,
    including view counting, moderation logic, and user association.
    """
    # 1. Retrieve the Post object.
    # Fetches a single post that matches the URL parameters and is published.
    # Raises a 404 error automatically if not found.
    post = get_object_or_404(Post,
                             status='published',
                             published_date__year=year,
                             published_date__month=month,
                             published_date__day=day,
                             slug=slug)

    # 2. Increment the View Count.
    # This uses an F() expression for a race-condition-safe database update.
    post.views_count = F('views_count') + 1
    post.save(update_fields=['views_count'])
    # Refresh the object from the DB to get the latest view count.
    post.refresh_from_db()

    # 3. Prepare for Comment Handling.
    # Get all approved, top-level comments for this post to display.
    comments = post.comments.filter(is_approved=True)
    
    # Get the site-wide configuration.
    try:
        site_config = SiteConfiguration.objects.get()
    except SiteConfiguration.DoesNotExist:
        # Fallback to a default config object if none exists in DB
        # This makes the site resilient even if setup is incomplete.
        class FallbackConfig:
            auto_approve_comments = False
        site_config = FallbackConfig()
    
    # This logic handles both GET requests and form submissions (POST).
    if request.method == 'POST':
        # If form is submitted, bind POST data and the request user to a form instance.
        comment_form = CommentForm(request.POST, user=request.user)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            
            # Associate comment with the logged-in user, if any.
            if request.user.is_authenticated:
                new_comment.user = request.user
                new_comment.author_name = request.user.profile.get_display_name()
                new_comment.author_email = request.user.email

            # Set approval status based on the site configuration.
            if site_config.auto_approve_comments:
                new_comment.is_approved = True
                success_message = gettext("Thank you! Your comment has been published.")
            else:
                new_comment.is_approved = False
                success_message = gettext("Thank you! Your comment has been submitted and is awaiting moderation.")

            new_comment.save()
            messages.success(request, success_message)
            
            # Use the Post/Redirect/Get pattern to prevent form resubmission.
            post_url = post.get_absolute_url()
            redirect_url = f"{post_url}#comments-section"
            return HttpResponseRedirect(redirect_url)
        else:
            # If the form is invalid, log the errors for debugging.
            logger.warning(f"Invalid comment submission on post '{post.slug}'. Errors: {comment_form.errors.as_json()}")
    else:
        # For a GET request, create a blank form instance, passing the user.
        comment_form = CommentForm(user=request.user)

    # 4. Prepare the final context and render the template.
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post_detail.html', context)


def posts_by_category_view(request, category_slug):
    """
    Filters and displays a paginated list of published posts
    belonging to a specific blog category.
    """
    # --- 1. Get Base Data ---
    category = get_object_or_404(PostCategory, slug=category_slug)
    all_posts_in_category = category.posts.filter(status='published').order_by('-published_date')

    # --- 2. Get Pagination Settings ---
    try:
        config = SiteConfiguration.objects.get()
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
    context = {
        'category': category,
        'posts': posts,  # Pass the paginated 'posts' object
    }
    return render(request, 'blog/post_list_by_category.html', context)

