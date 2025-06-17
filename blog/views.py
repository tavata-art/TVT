from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext

from .forms import CommentForm
from .models import Post, PostCategory, Comment
from site_settings.models import SiteConfiguration

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
        posts_per_page = 6  # Fallback
    paginator = Paginator(all_posts, posts_per_page)

    # 3. Get the page number from the URL's GET parameters (e.g., /blog/?page=2).
    page_number = request.GET.get('page')

    # 4. Get the specific Page object for the requested page number.
    #    This includes robust error handling.
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If the 'page' parameter is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If the page number is out of range (e.g., 999),
        # deliver the last page of results.
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
    Displays a single blog post, its comments, and handles new comment submissions.
    """
    # 1. Retrieve the main Post object
    # ---------------------------------
    # Fetches a single post that matches the URL parameters and is published.
    # Raises a 404 error automatically if not found.
    post = get_object_or_404(Post,
                             status='published',
                             published_date__year=year,
                             published_date__month=month,
                             published_date__day=day,
                             slug=slug)

    # 2. Increment the View Count
    # ---------------------------------
    # Uses an F() expression for a race-condition-safe, atomic database update.
    post.views_count = F('views_count') + 1
    post.save(update_fields=['views_count'])
    # Refreshes the object from the database to get the latest view count.
    post.refresh_from_db()

    # 3. Handle Comment Submission and Retrieval
    # -------------------------------------------
    # Get the site-wide configuration settings.
    site_config = SiteConfiguration.objects.get()
    
    # Retrieve all approved comments for this post to display.
    comments = post.comments.filter(is_approved=True)
    
    # Initialize the form.
    comment_form = CommentForm()

    if request.method == 'POST':
        # If the form was submitted, bind the POST data to the form.
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            # Create a Comment object but don't save to the DB yet.
            new_comment = comment_form.save(commit=False)
            # Associate the comment with the current post.
            new_comment.post = post
            
            # Set the approval status based on the site configuration.
            if site_config.auto_approve_comments:
                new_comment.is_approved = True
                success_message = gettext("Thank you! Your comment has been published.")
            else:
                new_comment.is_approved = False
                success_message = gettext("Thank you! Your comment has been submitted and is awaiting moderation.")

            # Now, save the comment to the database.
            new_comment.save()

            # Add the success message to be displayed on the next page load.
            messages.success(request, success_message)
            
            # --- Post/Redirect/Get Pattern ---
            # Redirect to the same page to prevent form resubmission on refresh.
            # Add an HTML anchor to scroll the user down to the comments section.
            post_url = post.get_absolute_url()
            redirect_url = f"{post_url}#comments-section"
            return HttpResponseRedirect(redirect_url)

    # 4. Prepare the Context and Render
    # ---------------------------------
    # This context is used for GET requests or when a POST form is invalid.
    # If the form was invalid, 'comment_form' will contain error messages to display.
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
        posts_per_page = 6  # Fallback

    # --- 3. Apply Pagination ---
    paginator = Paginator(all_posts_in_category, posts_per_page)
    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # --- 4. Prepare Context and Render ---
    context = {
        'category': category,
        'posts': posts,  # Pass the paginated 'posts' object
    }
    return render(request, 'blog/post_list_by_category.html', context)

