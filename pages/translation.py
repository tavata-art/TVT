# pages/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Page, Category

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description')
    
@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'content')