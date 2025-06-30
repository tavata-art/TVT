# File: posts/urls.py
from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path('', views.post_list_view, name='post_list'),
    
    # URL con fecha + slug
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail_view, name='post_detail'),
    path('category/<slug:category_slug>/', views.posts_by_category_view, name='posts_by_category'),
    path('tag/<slug:tag_slug>/', views.posts_by_tag_view, name='posts_by_tag'),
]
