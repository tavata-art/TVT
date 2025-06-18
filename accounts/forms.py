# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    """
    A custom user creation form to enhance styling and user experience.
    It inherits from Django's base UserCreationForm to maintain security features.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",) # We only request the username on the base form.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove the default help text that lists all password validators.
        # This allows us to provide a cleaner UI in the template.
        self.fields['password2'].help_text = None
        
        # Add Bootstrap classes and placeholders to the field widgets.
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Choose a username')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Enter password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': _('Confirm password')
        })

        # Customize field labels for clarity and translation.
        self.fields['username'].label = _('Username')
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Confirm Password')