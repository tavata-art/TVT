# File: pages/admin.py
import logging
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Required for dynamically generating search fields

# Third-party imports
from django_summernote.admin import SummernoteModelAdmin # For WYSIWYG editor on Page
from modeltranslation.admin import TabbedTranslationAdmin # For multilingual admin
from modeltranslation.translator import translator # Required for dynamic fields

# Local application imports (ensure these models exist in pages.models, categories.models)
from .models import Page 
from categories.models import Category # Universal Category model


logger = logging.getLogger(__name__)


# Helper function to dynamically generate search_fields and prepopulated_fields
# This is a re-use of the logic from blog/admin.py
def get_language_aware_admin_fields(model_kls):
    search_fields_list = []
    prepopulated_fields_dict = {}
    
    trans_opts = None
    try:
        trans_opts = translator.get_options_for_model(model_kls)
    except translator.NotRegistered:
        logger.warning(f"Model {model_kls.__name__} not registered for translation. Dynamic admin fields might be incomplete.")
        pass 

    for lang_code, _ in settings.LANGUAGES:
        if trans_opts:
            # Assuming 'title' and 'content' are common translatable fields
            if 'title' in trans_opts.fields:
                search_fields_list.append(f'title_{lang_code}')
            if 'content' in trans_opts.fields:
                search_fields_list.append(f'content_{lang_code}')
        
        # Consistent prepopulated_fields for slug based on title
        if hasattr(model_kls, 'slug') and hasattr(model_kls, f'title_{lang_code}'): 
            prepopulated_fields_dict[f'slug_{lang_code}'] = (f'title_{lang_code}',)
            
    return tuple(search_fields_list), prepopulated_fields_dict


# --- ADMIN FOR UNIVERSAL CATEGORIES ---
# This part is for the Category model in the categories app, not in pages app.
# Ensure this is defined in categories/admin.py, not here.


# --- ADMIN FOR PAGES ---
@admin.register(Page)
class PageAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    """
    Admin options for the Page model, integrating Summernote for content,
    ModelTranslation for multilingual fields, and managing categories.
    """
    # What fields to display in the list view
    list_display = ('title', 'status', 'is_homepage', 'importance_order', 'author', 'display_categories_list')
    
    # Allow editing these fields directly from the list view
    list_editable = ('status', 'is_homepage', 'importance_order') # Removed 'author' if it's a many-to-many relationship
    
    # Filters in the right sidebar
    list_filter = ('status', 'author', 'categories', 'is_homepage')
    
    # Generate search_fields and prepopulated_fields dynamically
    _search_fields, _prepopulated_fields = get_language_aware_admin_fields(Page)
    search_fields = _search_fields
    prepopulated_fields = _prepopulated_fields
    
    # Default ordering for the list
    ordering = ('importance_order', '-updated_at')
    
    # ManyToManyField for categories, uses a nice multi-selector interface
    filter_horizontal = ('categories',) 
    
    # Summernote fields must be specified for each language (e.g., 'content_en')
    summernote_fields = tuple([f'content_{lang_code}' for lang_code, _ in settings.LANGUAGES])


    # Custom method to display categories in the list view
    @admin.display(description=_("Categories"))
    def display_categories_list(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])