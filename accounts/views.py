# File: accounts/views.py
import logging
import os
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings 
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm

# Import the models required for the public profile view
from .models import Profile # Model for user profiles
from blog.models import Post, Comment # Models for posts and comments

from site_settings.models import SiteConfiguration 

# Get a logger instance for this module.
logger = logging.getLogger(__name__)
User = get_user_model()

# --- SIGNUP VIEW ---
def signup_view(request):
    """ Handles new user registration. """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"New user account created: '{user.username}' (ID: {user.id})")
            login(request, user)
            messages.success(request, gettext("Welcome! Your account has been created successfully."))
            return redirect('home')
        else:
            logger.warning(f"Signup form failed validation. Errors: {form.errors.as_json()}")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/signup.html', {'form': form})


@login_required 
def profile_edit_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Guardamos el formulario de usuario, que es simple.
            user_form.save()
            
            # --- LÓGICA FINAL Y EXPLÍCITA DE AVATAR ---
            profile = request.user.profile

            # Caso 1: El usuario subió una nueva imagen.
            if 'avatar' in request.FILES:
                uploaded_file = request.FILES['avatar']
                # Construimos el nuevo nombre de archivo
                extension = os.path.splitext(uploaded_file.name)[1]
                new_filename = f"avatars/{uuid.uuid4().hex}{extension}"
                
                # Si ya existe una imagen personalizada, la borramos para no dejar basura.
                if profile.avatar and os.path.exists(profile.avatar.path):
                    default_paths = [c[0] for c in profile.AvatarChoice.choices]
                    if profile.avatar.name not in default_paths:
                        os.remove(profile.avatar.path)
                
                # Guardamos el nuevo archivo con el nuevo nombre.
                profile.avatar.save(new_filename, uploaded_file)
                logger.info(f"User '{request.user.username}' uploaded new avatar, saved as {new_filename}")
            
            # Caso 2: El usuario marcó "Limpiar".
            elif profile_form.cleaned_data.get('avatar-clear'):
                chosen_default = profile_form.cleaned_data.get('default_avatar_choice')
                profile.avatar = chosen_default
                logger.info(f"User '{request.user.username}' cleared avatar, reverting to {chosen_default}")

            # Actualizamos los otros campos del perfil desde los datos validados del formulario
            profile.display_name = profile_form.cleaned_data['display_name']
            profile.bio = profile_form.cleaned_data['bio']
            profile.location = profile_form.cleaned_data['location']
            profile.website_url = profile_form.cleaned_data['website_url']
            
            # Si no se limpió el avatar, la elección por defecto también se guarda
            if not profile_form.cleaned_data.get('avatar-clear'):
                 profile.default_avatar_choice = profile_form.cleaned_data.get('default_avatar_choice')
            
            profile.save() # Guardamos todos los cambios en el objeto profile
            
            messages.success(request, gettext("Your profile has been updated successfully!"))
            return redirect('accounts:profile_edit')
            
        else:
            logger.warning("Profile update form failed validation.", extra={'errors': profile_form.errors.as_json()})

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'registration/profile_edit.html', context)

def user_profile_public_view(request, username):
    """
    Displays public information for a given user, including their profile details
    and a paginated list of their public contributions (posts, comments).
    """
    try:
        # Get the user by username, or return a 404
        user_obj = get_object_or_404(User, username=username)
        # Ensure the user has an associated profile
        if not hasattr(user_obj, 'profile') or user_obj.profile is None:
            logger.warning(f"User '{username}' does not have an associated profile. Creating one.")
            # This should ideally not happen due to the signal, but as a failsafe
            profile = user_obj.profile = Profile.objects.create(user=user_obj)
        else:
            profile = user_obj.profile

        logger.info(f"Public profile view accessed for user: '{username}'.")

        # --- User's Blog Posts (Publicly visible) ---
        user_posts = Post.objects.filter(
            author=user_obj, 
            status='published'
        ).order_by('-published_date')

        # --- User's Comments (Approved and publicly visible) ---
        user_comments = Comment.objects.filter(
            user=user_obj, 
            is_approved=True
        ).order_by('-created_at')

        site_config = SiteConfiguration.get_solo()
        items_per_page = getattr(site_config, 'user_profile_items_per_page', 5) # Fallback to 5


        # Paginate Posts
        posts_paginator = Paginator(user_posts, items_per_page)
        posts_page_number = request.GET.get('posts_page', 1)
        paginated_user_posts = posts_paginator.get_page(posts_page_number)

        # Paginate Comments
        comments_paginator = Paginator(user_comments, items_per_page)
        comments_page_number = request.GET.get('comments_page', 1)
        paginated_user_comments = comments_paginator.get_page(comments_page_number)

        context = {
            'user_obj': user_obj, # The User object
            'profile': profile,   # The associated Profile object
            'user_posts': paginated_user_posts,
            'user_comments': paginated_user_comments,
        }
        return render(request, 'accounts/public_profile_view.html', context)

    except User.DoesNotExist:
        logger.warning(f"Public profile requested for non-existent user: '{username}'.")
        raise
    except Exception as e:
        logger.error(f"Error accessing public profile for user '{username}': {e}", exc_info=True)
        raise # Re-raise for Django to handle 500 error page

def user_directory_view(request):
    """
    Displays a paginated list of all active users in the system.
    """
    # 1. Get all active users, ordered by username.
    # You might want to filter out staff/superusers if you don't want them listed.
    all_users = User.objects.filter(
        is_active=True,
        profile__is_listed_publicly=True
    ).order_by('username')
    
    # 2. Get pagination settings.
    try:
        site_config = SiteConfiguration.get_solo()
        items_per_page = getattr(site_config, 'user_directory_items_per_page', 25)
    except SiteConfiguration.DoesNotExist:
        items_per_page = 25
        logger.warning("SiteConfiguration not found. Using default user directory items per page (25).")

    # 3. Apply pagination.
    paginator = Paginator(all_users, items_per_page)
    page_number = request.GET.get('page')

    try:
        users_on_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        users_on_page = paginator.get_page(1)
    except EmptyPage:
        if paginator.num_pages > 0:
            users_on_page = paginator.get_page(paginator.num_pages)
        else:
            users_on_page = []

    logger.info(f"User directory view accessed. Showing page {getattr(users_on_page, 'number', 0)} of {getattr(users_on_page, 'paginator.num_pages', 0)} users.")

    context = {
        'users': users_on_page, # Pass the paginated user objects
    }
    return render(request, 'accounts/user_directory.html', context)