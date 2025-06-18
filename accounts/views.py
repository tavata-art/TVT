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
    """
    Handles the display and submission of the user and profile update forms,
    including logic for a custom "clear avatar" checkbox.
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the User form data first.
            user_form.save()
            
            # --- FINAL AVATAR LOGIC ---
            # Get the profile object from the form but don't save it to the DB yet.
            profile = profile_form.save(commit=False)
            
            # Check the value of our custom 'clear_avatar' checkbox.
            clear_avatar_checked = profile_form.cleaned_data.get('clear_avatar')

            # Scenario 1: User explicitly checked the box to revert to a default avatar.
            if clear_avatar_checked:
                chosen_default = profile_form.cleaned_data.get('default_avatar_choice')
                profile.avatar = chosen_default  # This assigns the text path to the default image
                logger.info(f"User '{request.user.username}' explicitly cleared avatar, reverting to {chosen_default}")
            
            # Scenario 2: User uploaded a new file.
            # The ModelForm has already handled this and updated the `profile.avatar`
            # field in memory. We don't need an explicit elif.
            elif 'avatar' in request.FILES:
                 logger.info(f"User '{request.user.username}' uploaded a new avatar.")

            # Scenario 3: User did neither. The existing avatar remains untouched.

            # Finally, save the profile instance with all changes to the database.
            profile.save()
            # --- END OF LOGIC ---

            messages.success(request, gettext("Your profile has been updated successfully!"))
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