from modeltranslation.translator import translator, TranslationOptions
from .models import Image

class ImageTranslationOptions(TranslationOptions):
    fields = ('title',)

translator.register(Image, ImageTranslationOptions)