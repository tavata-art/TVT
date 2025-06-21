from django.contrib import admin
from .models import Image
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin

@admin.register(Image)
class ImageAdmin(TabbedTranslationAdmin):
    list_display = (
        'get_translated_title', 
        'uploaded_at', 
        'image'
    )

    def get_translated_title(self, obj):
        return obj.title
    get_translated_title.short_description = _('Title')