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


# --- PROFILE EDIT VIEW ---
@login_required 
def profile_edit_view(request):
    """
    Handles the display and submission of the forms for updating
    both the User model and its related Profile model.
    The view's role is to validate and save the forms. The model handles the logic
    for which avatar URL to display.
    """
    if request.method == 'POST':
        # Bind submitted data to form instances, linked to the current user.
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            # If both forms are valid, save them directly.
            # The ProfileUpdateForm will save the user's choice for 'default_avatar_choice'.
            # If a new avatar file was uploaded, it will also be saved automatically.
            user_form.save()
            profile_form.save()

            logger.info(f"User '{request.user.username}' updated their profile successfully.")
            messages.success(request, gettext("Your profile has been updated successfully!"))
            
            # Redirect to the same page to show changes and prevent resubmission.
            return redirect('accounts:profile_edit')
        else:
            logger.warning(f"Profile update failed for user '{request.user.username}'. "
                           f"User form errors: {user_form.errors.as_json()}, "
                           f"Profile form errors: {profile_form.errors.as_json()}.")
    else:
        # For a GET request, create forms pre-filled with the user's current data.
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'registration/profile_edit.html', context)