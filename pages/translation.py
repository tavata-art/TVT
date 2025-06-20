# pages/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Page
    
@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content', 'meta_title', 'meta_description')