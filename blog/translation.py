# blog/translation.py   
from modeltranslation.translator import register, TranslationOptions
from .models import Post, PostCategory, Comment

@register(PostCategory)
class PostCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'meta_title', 'meta_description')

@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content', 'meta_title', 'meta_description')

@register(Comment)
class CommentTranslationOptions(TranslationOptions):
    fields = ('content',)