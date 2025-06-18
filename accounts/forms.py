# File: accounts/forms.py
import logging
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Profile

logger = logging.getLogger(__name__)


# --- 1. Custom SIGNUP Form (for new user registration) ---
class CustomUserCreationForm(UserCreationForm):
    """
    A custom user creation form to enhance styling and user experience.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].help_text = None
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Choose a username')})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Enter password')})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Confirm password')})
        self.fields['username'].label = _('Username')
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Confirm Password')


# --- 2. Custom User UPDATE Form (for editing basic User data) ---
class UserUpdateForm(forms.ModelForm):
    """
    A form to update basic, non-sensitive user information like name and email.
    """
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add labels and placeholders for better UI
        self.fields['first_name'].label = _('First Name')
        self.fields['last_name'].label = _('Last Name')
        self.fields['email'].label = _('Contact Email')
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Your first name')})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Your last name')})


# --- 3. Custom Profile UPDATE Form (for editing extended Profile data) ---
class ProfileUpdateForm(forms.ModelForm):
    """
    A form to update the extended profile information, including the avatar.
    This form dynamically hides the default avatar choice if a custom one is uploaded.
    """
    class Meta:
        model = Profile
        fields = [
            'display_name', 
            'bio', 
            'location', 
            'website_url', 
            'avatar', 
            'default_avatar_choice'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- Add Bootstrap classes to all widgets ---
        self.fields['display_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['bio'].widget.attrs.update({'class': 'form-control', 'rows': 4})
        self.fields['location'].widget.attrs.update({'class': 'form-control'})
        self.fields['website_url'].widget.attrs.update({'class': 'form-control', 'placeholder': 'https://...'})
        self.fields['avatar'].widget.attrs.update({'class': 'form-control'}) # For file inputs
        
        # --- Smart logic for the default avatar choice field ---
        # The 'self.instance' is the Profile object being edited.
        # We only run this logic if the form is bound to an existing Profile.
        if self.instance and self.instance.pk:
            current_avatar_path = self.instance.avatar.name
            default_avatar_path = self.instance._meta.get_field('avatar').get_default()

            # If the user's current avatar is NOT the default one...
            if current_avatar_path != default_avatar_path:
                # ...then we don't need to show the default avatar choice field.
                # We remove it dynamically from the form.
                del self.fields['default_avatar_choice']
            else:
                # If they are using a default avatar, style the dropdown.
                self.fields['default_avatar_choice'].widget.attrs.update({'class': 'form-select'})
        else:
            # If this is a new, unbound form, style the dropdown by default.
            self.fields['default_avatar_choice'].widget.attrs.update({'class': 'form-select'})

        logger.debug(f"ProfileUpdateForm initialized for instance: {self.instance}")