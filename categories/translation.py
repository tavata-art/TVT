# File: categories/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Category

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    # ANTES: fields = ('name', 'slug', 'meta_title', 'meta_description')
    # AHORA:
    fields = ('name', 'slug', 'description', 'meta_title', 'meta_description')