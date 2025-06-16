# Add get_object_or_404 and PostCategory back to the imports
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Post, PostCategory, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F
from .forms import CommentForm

def post_list_view(request):
    """
    Displays a list of published blog posts, paginated.
    """
    # 1. Retrieve the full, ordered list of all published posts.
    all_posts = Post.objects.filter(status='published').order_by('-published_date')

    # 2. Create a Paginator instance.
    #    We'll show 6 posts per page. This number can be changed easily.
    paginator = Paginator(all_posts, 6)

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
    Displays a single blog post and handles the comment submission process.
    """
    # 1. Retrieve the Post object
    # ---------------------------------
    # We fetch a single post that matches the URL parameters and is published.
    # If no post is found, it will automatically raise a 404 error.
    post = get_object_or_404(Post, 
                             status='published',
                             published_date__year=year,
                             published_date__month=month,
                             published_date__day=day,
                             slug=slug)

    # 2. Increment the View Count
    # ---------------------------------
    # We use an F() expression to perform an atomic update on the database,
    # which is safe from race conditions and efficient.
    post.views_count = F('views_count') + 1
    post.save(update_fields=['views_count'])
    # We refresh the object from the database to get the updated view count
    # immediately available in the template if needed.
    post.refresh_from_db()

    # 3. Handle the Comment Form
    # ---------------------------------
    # Get all approved comments for this post.
    # The 'comments' related_name comes from the ForeignKey in the Comment model.
    comments = post.comments.filter(is_approved=True)
    
    # Initialize the form instance.
    comment_form = CommentForm()

    if request.method == 'POST':
        # If the request is a POST, a comment has been submitted.
        # We bind the submitted data to a new form instance.
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            # If the form is valid, create a Comment object but don't save it yet.
            new_comment = comment_form.save(commit=False)
            # Associate the comment with the current post.
            new_comment.post = post
            # For testing, we approve comments automatically. In production, this would be False.
            new_comment.is_approved = True
            # Now, save the comment to the database.
            new_comment.save()

            # --- Post/Redirect/Get Pattern ---
            # We redirect to the same page to prevent form resubmission on refresh.
            # We add an HTML anchor to scroll the user down to the comments section.
            post_url = post.get_absolute_url()
            redirect_url = f"{post_url}#comments-section"
            return HttpResponseRedirect(redirect_url)
    
    # 4. Prepare the Context and Render
    # ---------------------------------
    # This part is reached on a GET request, or if a POST form is invalid.
    # If the form was invalid, 'comment_form' will contain the errors to display.
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post_detail.html', context)


# --- NUEVA VISTA PARA CATEGORÍAS ---
def posts_by_category_view(request, category_slug):
    """
    Filtra y muestra todas las entradas publicadas que pertenecen
    a una categoría de blog específica.
    """
    # 1. Obtenemos el objeto de la categoría; si no existe, 404.
    category = get_object_or_404(PostCategory, slug=category_slug)

    # 2. Filtramos los posts usando el 'related_name="posts"'.
    #    Solo queremos los que estén publicados.
    posts = category.posts.filter(status='published')

    # 3. Preparamos el contexto.
    context = {
        'category': category,
        'posts': posts, # Le pasamos la lista de posts filtrados
    }

    # 4. Renderizamos la plantilla.
    return render(request, 'blog/post_list_by_category.html', context)

