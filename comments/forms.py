# File: comments/forms.py

from django import forms
from .models import Comment
from django.utils.translation import gettext_lazy as _

class CommentForm(forms.ModelForm):
    """
    ✏️ Public comment form shown on post detail pages.
    Only allows name, email and content.
    """

    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'content']
        labels = {
            'author_name': _("Your name"),
            'author_email': _("Your email"),
            'content': _("Comment"),
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
