from modeltranslation.translator import register, TranslationOptions
from .models import SiteConfiguration

@register(SiteConfiguration)
class SiteConfigurationTranslationOptions(TranslationOptions):
    fields = ('site_slogan',)