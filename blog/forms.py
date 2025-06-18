# File: blog/forms.py
import logging
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Comment

# Get a logger instance for this module
logger = logging.getLogger(__name__)

class CommentForm(forms.ModelForm):
    """
    A form for users to submit comments.
    It dynamically adjusts fields based on whether the user is authenticated.
    """

    class Meta:
        model = Comment
        # The user will fill out these fields.
        # 'parent' is for handling replies and will be a hidden field.
        # 'user' and 'post' will be assigned in the view.
        fields = ['content', 'parent', 'author_name', 'author_email']
        
        # We use a HiddenInput for the 'parent' field. Its value will be set by JavaScript.
        widgets = {
            'parent': forms.HiddenInput(),
        }


    def __init__(self, *args, **kwargs):
        # We pop the 'user' object passed from the view.
        # It will be None if the user is not authenticated.
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # --- Customize fields with Bootstrap classes and placeholders ---
        self.fields['content'].widget = forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4,
            'placeholder': _('Write your comment here...')
        })
        self.fields['author_name'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Name (required)')
        })
        self.fields['author_email'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Email (required, not published)')
        })
        
        # --- Dynamic field logic based on user authentication ---
        if self.user and self.user.is_authenticated:
            # If the user is logged in, we don't need them to enter their name and email.
            # We hide these fields and make them not required.
            self.fields['author_name'].required = False
            self.fields['author_email'].required = False
            
            # Instead of removing them, we turn them into hidden fields.
            # This way, the view can still populate them with the user's data for consistency.
            self.fields['author_name'].widget = forms.HiddenInput()
            self.fields['author_email'].widget = forms.HiddenInput()
            
            # Log that we are customizing the form for a logged-in user.
            logger.debug(f"Customizing CommentForm for authenticated user: {self.user.username}")


    def clean(self):
        # We log form errors to help with debugging validation issues.
        if self.errors:
            logger.warning(f"CommentForm validation failed. Errors: {self.errors.as_json()}")
        return super().clean()