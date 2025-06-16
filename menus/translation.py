# menus/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Menu, MenuItem

# ==============================================================================
# 1. Register the Menu model for translation.
#    This makes the 'title' field multilingual.
# ==============================================================================
@register(Menu)
class MenuTranslationOptions(TranslationOptions):
    """ Translation options for the Menu model. """
    fields = ('title',)


# ==============================================================================
# 2. Register the MenuItem model for translation.
#    This makes the 'title' field of each link multilingual.
# ==============================================================================
@register(MenuItem)
class MenuItemTranslationOptions(TranslationOptions):
    """ Translation options for the MenuItem model. """
    fields = ('title',)