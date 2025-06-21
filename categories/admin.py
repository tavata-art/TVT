# File: categories/admin.py
import logging
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.conf import settings 

# Third-party imports
from mptt.admin import DraggableMPTTAdmin 
from modeltranslation.admin import TabbedTranslationAdmin
from modeltranslation.translator import translator 

# Local application imports (ensure this model exists in categories.models)
from .models import Category


logger = logging.getLogger(__name__)


# Helper function to dynamically generate prepopulated_fields for multi-language slugs.
def get_language_aware_prepopulated_fields(model_kls):
    prepopulated_fields_dict = {}
    trans_opts = None
    try:
        trans_opts = translator.get_options_for_model(model_kls)
    except translator.NotRegistered:
        logger.warning(f"Model {model_kls.__name__} not registered for translation. "
                       f"Dynamic prepopulated_fields might be incomplete.")
        return prepopulated_fields_dict 

    has_slug = hasattr(model_kls, 'slug')
    has_translatable_name = 'name' in trans_opts.fields if trans_opts else False

    if has_slug and has_translatable_name:
        for lang_code, _ in settings.LANGUAGES:
            prepopulated_fields_dict[f'slug_{lang_code}'] = (f'name_{lang_code}',)
                
    return prepopulated_fields_dict


# Helper function to dynamically generate search_fields for translatable models.
def get_language_aware_search_fields(model_kls):
    """
    Generates a tuple of search fields for a model in all configured languages.
    Assumes 'name' and 'description' are common translatable text fields.
    """
    search_fields_list = []
    trans_opts = None
    try:
        trans_opts = translator.get_options_for_model(model_kls)
    except translator.NotRegistered:
        return tuple() 

    for lang_code, _ in settings.LANGUAGES:
        if 'name' in trans_opts.fields:
            search_fields_list.append(f'name_{lang_code}')
        if 'description' in trans_opts.fields: # Assuming description is also a common searchable field
            search_fields_list.append(f'description_{lang_code}')

    return tuple(search_fields_list)


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin, DraggableMPTTAdmin):
    """
    Admin options for the universal Category model.
    It combines TabbedTranslationAdmin for multilingual fields
    and DraggableMPTTAdmin for intuitive drag-and-drop hierarchy management.
    """
    
    # --- MPTT Configuration ---
    list_display = (
        'tree_actions',    
        'indented_title',  
        'slug',            
        # --- REMOVE THIS LINE ---
        # get_language_aware_search_fields.description # This line caused the error!
    )
    list_display_links = ('indented_title',) 

    mptt_level_indent = 20 

    # --- ModelTranslation Configuration ---
    prepopulated_fields = get_language_aware_prepopulated_fields(Category)
    
    # --- Standard Django Admin Configuration ---
    search_fields = get_language_aware_search_fields(Category)
    
    # --- Optional: Custom field for post count (ensure blog_posts is defined in models.py) ---
    # @admin.display(description=_("Post Count"))
    # def post_count_display(self, obj):
    #     return obj.blog_posts.count() if hasattr(obj, 'blog_posts') else 0
    # list_display = list_display + ('post_count_display',) # Add to list_display if you uncomment