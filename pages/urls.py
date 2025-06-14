# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # NUEVA RUTA: Recibirá un 'slug' de categoría como parámetro
    # Ejemplo: /pages/category/tutoriales/
    path('category/<slug:category_slug>/', views.pages_by_category_view, name='pages_by_category'),

    # Ruta existente para el detalle de una página
    # Ejemplo: /pages/sobre-nosotros/
    path('<slug:slug>/', views.page_detail_view, name='page_detail'),
]