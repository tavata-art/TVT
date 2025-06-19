# pages/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Page, Category

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description', 'meta_title', 'meta_description')
    
@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content', 'meta_title', 'meta_description')