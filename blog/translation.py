# File: blog/translation.py
from modeltranslation.translator import register, TranslationOptions
# Solo importamos los modelos que SÍ existen en blog.models
from .models import Post, Comment 
from taggit.models import Tag 

# La clase para PostCategory ha sido eliminada.

@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content', 'meta_title', 'meta_description')

@register(Comment)
class CommentTranslationOptions(TranslationOptions):
    fields = ('content',)

@register(Tag)
class TagTranslationOptions(TranslationOptions):
    """
    Registers django-taggit's Tag model for translation,
    making tag names multilingual.
    """
    fields = ('name',)