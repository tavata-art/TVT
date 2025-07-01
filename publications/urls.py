# File: publications/urls.py
from django.urls import path
from .views import publication_detail_view

app_name = "publications"

urlpatterns = [
    path('<slug:slug>/', publication_detail_view, name='publication_detail'),
]