# File: accounts/views.py
import logging
import os
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm

# Get a logger instance for this module.
logger = logging.getLogger(__name__)


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