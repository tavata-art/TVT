# blog/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        # We only want the user to fill these fields
        fields = ('author_name', 'author_email', 'content', 'parent')

        # Add some Bootstrap classes to the widgets for styling
        widgets = {
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Your Name')}),
            'author_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Your Email')}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Your Comment')}),
            # We'll hide the 'parent' field with CSS, it will be filled by JavaScript.
            'parent': forms.HiddenInput(attrs={'class': 'd-none'}),
        }
        labels = {
            'author_name': _('Name'),
            'author_email': _('Email'),
            'content': _('Comment'),
        }