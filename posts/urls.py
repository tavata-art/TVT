# File: posts/urls.py
from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path('', views.post_list_view, name='post_list'),
    
    # URL con fecha + slug
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail_view, name='post_detail'),
]
