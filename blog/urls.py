# blog/urls.py
from django.urls import path
from . import views

# Esto es importante para evitar colisiones de nombres de URL con otras apps
app_name = 'blog'

urlpatterns = [
    # 1. La URL raíz del blog, que mostrará la lista de posts
    # Ejemplo: /blog/
    path('', views.post_list_view, name='post_list'),

    # ¡NUEVA RUTA! Para listar posts de una categoría específica
    # Ejemplo: /blog/category/desarrollo-web/
    path('category/<slug:category_slug>/', views.posts_by_category_view, name='posts_by_category'),
    
    # 2. La URL para un post individual, usando año, mes, día y slug
    # Ejemplo: /blog/2025/06/15/mi-primer-post/
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail_view, name='post_detail'),
]