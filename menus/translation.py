# menus/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import MenuItem

@register(MenuItem)
class MenuItemTranslationOptions(TranslationOptions):
    fields = ('title',)