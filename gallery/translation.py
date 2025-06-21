# File: gallery/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Image

@register(Image)
class ImageTranslationOptions(TranslationOptions):
    fields = ('title', 'description',) # Include 'description' for translation