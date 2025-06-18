# accounts/views.py
import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required # ¡Importante!
from django.utils.translation import gettext
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm 


# Get a logger instance for this module.
logger = logging.getLogger(__name__)

def signup_view(request):
    """
    Handles new user registration, including form validation and success/error logging.
    """
    if request.method == 'POST':
        # If the form is submitted, bind POST data to our custom form.
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            # If the form is valid, save the new user to the database.
            # This automatically handles password hashing.
            user = form.save()
            
            # Log the successful creation of a new user account.
            # This is an important security and auditing event.
            logger.info(f"New user account created: '{user.username}' (ID: {user.id})")
            
            # Log the user in immediately after successful registration.
            login(request, user)
            
            # Create a success flash message for the user.
            success_message = gettext("Welcome! Your account has been created successfully.")
            messages.success(request, success_message)
            
            # Redirect to the homepage.
            return redirect('home') # Use the URL name for more robust routing
    else:
        # For a GET request, create a blank form instance.
        form = CustomUserCreationForm()
        
    return render(request, 'registration/signup.html', {'form': form})

# --- NEW VIEW FOR EDITING THE PROFILE ---
@login_required # This decorator ensures only logged-in users can access this view
def profile_edit_view(request):
    """
    Handles the display and submission of the user and profile update forms.
    """
    if request.method == 'POST':
        # If the form is submitted, bind the POST data and FILES data to the forms.
        # We pass 'instance=request.user' to update the existing user.
        user_form = UserUpdateForm(request.POST, instance=request.user)
        # We pass 'instance=request.user.profile' to update the existing profile.
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        # Both forms must be valid to proceed.
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            #
            logger.info(f"User '{request.user.username}' updated their profile successfully.")

            # Create a success flash message.
            success_message = gettext("Your profile has been updated successfully!")
            messages.success(request, success_message)

            # Redirect back to the same page to show the changes.
            return redirect('accounts:profile_edit')

        else:
            # If any form is invalid, log the errors.
            logger.warning(f"Profile update failed for user '{request.user.username}'. "
                           f"User form errors: {user_form.errors.as_json()}. "
                           f"Profile form errors: {profile_form.errors.as_json()}.")

    else:
        # For a GET request, create form instances pre-filled with the user's current data.
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'registration/profile_edit.html', context)