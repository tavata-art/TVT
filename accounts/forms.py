# File: accounts/forms.py
import logging
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from widgets.widgets import CustomClearableFileInput
from .models import Profile

logger = logging.getLogger(__name__)


# --- 1. Custom SIGNUP Form (for new user registration) ---
class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for new user registration. It only handles User model fields.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        # The 'fields' tuple should only contain fields from the User model.
        # 'password1' and 'password2' are handled automatically by UserCreationForm.
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
    A form for updating basic, non-sensitive user information.
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
        self.fields['first_name'].label = _('First Name')
        self.fields['last_name'].label = _('Last Name')
        self.fields['email'].label = _('Contact Email')
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Your first name')})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Your last name')})


# --- 3. Custom Profile UPDATE Form (for editing extended Profile data) ---
class ProfileUpdateForm(forms.ModelForm):
    """
    A form for updating the extended profile, using a custom widget for the avatar.
    """
    # We explicitly define the avatar field to force our custom widget.
    avatar = forms.ImageField(
        label=_("Profile Picture"),
        required=False,
        widget=CustomClearableFileInput() # Custom widget for file input
    )
    clear_avatar = forms.BooleanField(
        label=_("Use default avatar"),
        required=False,
        # Le damos una clase de Bootstrap para que se vea bien
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = Profile
        fields = [
            'display_name', 
            'bio', 
            'location', 
            'website_url', 
            'avatar', 
            'default_avatar_choice',
            'is_listed_publicly'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Bootstrap classes to the rest of the fields.
        self.fields['display_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['bio'].widget.attrs.update({'class': 'form-control', 'rows': 4})
        self.fields['location'].widget.attrs.update({'class': 'form-control'})
        self.fields['website_url'].widget.attrs.update({'class': 'form-control', 'placeholder': 'https://...'})
        self.fields['default_avatar_choice'].widget.attrs.update({'class': 'form-select'})

        logger.debug(f"ProfileUpdateForm initialized for instance: {self.instance}")
