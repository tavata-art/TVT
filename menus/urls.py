from django.urls import path
from . import views

app_name = 'menus'

urlpatterns = [
    path('test/', views.menu_test_view, name='menu_test'),
]