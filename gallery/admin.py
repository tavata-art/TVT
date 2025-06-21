# File: gallery/admin.py
from django.contrib import admin
from .models import Image
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin
from django.conf import settings # NEW: Import settings
import logging

logger = logging.getLogger(__name__)

@admin.register(Image)
class ImageAdmin(TabbedTranslationAdmin):
    """
    Admin options for the Image model, integrating ModelTranslation for multilingual fields.
    Dynamically generates search_fields based on configured languages.
    """
    list_display = (
        'get_translated_title',  
        'image',                 
        'uploaded_at',           
    )
    list_filter = ('uploaded_at',) 
    ordering = ('-uploaded_at',) 

    # --- NEW: Dynamically generate search_fields ---
    # We create a list of all translatable fields (as defined in translation.py)
    # for each configured language.
    search_fields = []
    for lang_code, lang_name in settings.LANGUAGES:
        # Assuming 'title' and 'description' are the translatable fields for Image
        # as defined in gallery/translation.py
        search_fields.append(f'title_{lang_code}')
        search_fields.append(f'description_{lang_code}')
    # Convert the list to a tuple, as search_fields expects a tuple.
    search_fields = tuple(search_fields)
    # --- END NEW ---

    # Control which fields are editable in the form
    fields = ('title', 'description', 'image',) # Now 'title' and 'description' refer to the modeltranslation default fields (current language)

    # Custom method to display the translated title in the list view.
    @admin.display(description=_('Title'))
    def get_translated_title(self, obj):
        # obj.title automatically returns the translated title for the current admin language.
        return obj.title 
    
    def save_model(self, request, obj, form, change):
        """ Log when an image is saved or updated. """
        super().save_model(request, obj, form, change)
        if change:
            logger.info(f"Image '{obj.title}' (ID: {obj.id}) updated by {request.user.username}.")
        else:
            logger.info(f"New image '{obj.title}' (ID: {obj.id}) added by {request.user.username}.")
