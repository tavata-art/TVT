# blog/views.py
from django.shortcuts import render, get_object_or_404
from .models import Post, PostCategory

# --- Vista para la lista de posts ---
def post_list_view(request):
    # Obtenemos solo los posts que están publicados
    posts = Post.objects.filter(status='published')

    context = {
        'posts': posts,
    }
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

    context = {
        'post': post,
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

