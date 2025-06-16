# Add get_object_or_404 and PostCategory back to the imports
from django.shortcuts import render, get_object_or_404
from .models import Post, PostCategory
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


# --- Vista para el detalle de un post ---
def post_detail_view(request, year, month, day, slug):
    # Buscamos un post que coincida con todos los parámetros de la URL
    # y que esté publicado. Si no, devuelve un error 404.
    post = get_object_or_404(Post, 
                             status='published',
                             published_date__year=year,
                             published_date__month=month,
                             published_date__day=day,
                             slug=slug)

    # --- LÓGICA DE INCREMENTO DE VISTAS ---
    # Increment the view count by 1 efficiently in the database
    post.views_count = F('views_count') + 1
    post.save(update_fields=['views_count'])
    # Refresh the object from the database to get the updated value
    post.refresh_from_db()
    # --- FIN DE LA LÓGICA DE VISTAS ---
    
    # --- Lógica de Comentarios ---
    # 1. Get all approved comments for this post
    comments = post.comments.filter(is_approved=True)

    # 2. Form processing
    new_comment = None
    comment_form = CommentForm() # Create an empty form instance

    if request.method == 'POST':
        # If the form was submitted, create an instance with the submitted data
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create the comment object but don't save to the database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # We'll set is_approved to False in production for moderation
            new_comment.is_approved = True 
            # Save the comment to the database
            new_comment.save()
            # Reset the form after successful submission
            comment_form = CommentForm() 
    # --- Fin de Lógica de Comentarios ---

    context = {
        'post': post,
        'comments': comments,       # Pass the list of comments to the template
        'comment_form': comment_form, # Pass the form instance to the template
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

