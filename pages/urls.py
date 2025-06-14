# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La URL será /pages/mi-slug-de-pagina/
    path('<slug:slug>/', views.page_detail_view, name='page_detail'),
]