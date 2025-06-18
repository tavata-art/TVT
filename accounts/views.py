# accounts/views.py
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext

from .forms import CustomUserCreationForm

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