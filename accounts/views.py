# File: accounts/views.py
import logging
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
    """
    Handles new user registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"New user account created: '{user.username}' (ID: {user.id})")
            
            login(request, user)
            
            messages.success(request, gettext("Welcome! Your account has been created successfully."))
            return redirect('home')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/signup.html', {'form': form})


# --- PROFILE EDIT VIEW ---
@login_required 
def profile_edit_view(request):
    """
    Handles the display and submission of the user and profile update forms.
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            
            # Avatar sync logic
            if 'avatar' not in request.FILES:
                chosen_default = profile_form.cleaned_data.get('default_avatar_choice')
                if chosen_default and profile.avatar.name != chosen_default:
                    profile.avatar = chosen_default
            
            profile.save()

            messages.success(request, gettext("Your profile has been updated successfully!"))
            return redirect('accounts:profile_edit')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'registration/profile_edit.html', context)