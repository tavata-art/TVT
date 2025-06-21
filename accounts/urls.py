# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.user_profile_public_view, name='public_profile'),
    path('directory/', views.user_directory_view, name='user_directory'),
]