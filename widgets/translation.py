# widgets/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Widget

@register(Widget)
class WidgetTranslationOptions(TranslationOptions):
    fields = ('title',)