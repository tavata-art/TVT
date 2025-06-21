# File: menus/admin.py
import logging
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Required for dynamically accessing LANGUAGE_CODE

# Third-party imports
from mptt.admin import DraggableMPTTAdmin 
from modeltranslation.admin import TabbedTranslationAdmin
from modeltranslation.translator import translator, NotRegistered # NotRegistered is for helper function

# Local application imports
from .models import Menu, MenuItem # Ensure these models are defined in menus/models.py


logger = logging.getLogger(__name__)


# --- Helper functions for dynamic admin fields ---
# This helper is self-contained within this admin file for now.
# Ideally, for broader reuse across admin files, it could be moved to a shared utility module (e.g., core/admin_helpers.py).

def get_translated_fieldnames(field_base, model_kls=None):
    """
    Dynamically generates a list of translated field names (e.g., 'title_en', 'title_es', 'title_ca')
    for a given base field name (e.g., 'title'), based on Django project's LANGUAGES settings.

    Args:
        field_base (str): The base name of the field (e.g., 'title', 'content', 'description').
        model_kls (Model, optional): The model class to check if the field_base is
                                    actually translatable for that model. If not provided,
                                    it assumes the field could be translatable.
    Returns:
        tuple: A tuple of generated field names (e.g., ('title_en', 'title_es')).
    """
    generated_field_names = []
    
    # Check if the model_kls is provided and the field_base is indeed translatable for it.
    if model_kls:
        try:
            trans_opts = translator.get_options_for_model(model_kls)
            if field_base not in trans_opts.fields:
                # If the field is not registered for translation for this model,
                # return just the base field name as a single-element tuple.
                # This ensures backward compatibility if a non-translatable field is passed.
                return (field_base,) 
        except NotRegistered:
            # If the model itself is not registered for translation, return the base field.
            return (field_base,)

    # Generate translated field names for all configured languages.
    for lang_code, _ in settings.LANGUAGES:
        generated_field_names.append(f"{field_base}_{lang_code}")
    
    return tuple(generated_field_names)


# --- ADMIN FOR MAIN MENU CONTAINERS ---
@admin.register(Menu)
class MenuAdmin(TabbedTranslationAdmin):
    """
    Admin options for the main Menu containers (e.g., 'Main Menu', 'Footer Menu').
    This class handles the creation and top-level management of Menu objects.
    """
    list_display = ('title', 'slug') # 'title' is translatable, 'slug' is not.
    
    prepopulated_fields = {
        # The 'slug' field of the Menu model is NOT translatable, but its 'title' IS.
        # We prepopulate the non-translatable 'slug' from the 'title' field of the default language.
        'slug': (f'title_{settings.LANGUAGE_CODE}',)
    }

    # Search functionality over translated title fields.
    search_fields = get_translated_fieldnames('title', model_kls=Menu)

    # Note: MenuItem inline management is done via MenuItemAdmin directly for hierarchy.


# --- ADMIN FOR HIERARCHICAL MENU ITEMS ---
@admin.register(MenuItem)
class MenuItemAdmin(DraggableMPTTAdmin, TabbedTranslationAdmin):
    """
    Admin options for the hierarchical MenuItem model.
    This combines DraggableMPTTAdmin for intuitive drag-and-drop hierarchy management
    and TabbedTranslationAdmin for multilingual fields (like 'title').
    """
    # Fields to display in the tree view list of menu items.
    list_display = (
        'tree_actions',    # Provided by DraggableMPPTAAdmin for drag-and-drop handles.
        'indented_title',  # Provided by DraggableMPPTAAdmin to show indented title.
        'link_type',       # Displays the chosen link type (e.g., 'Page', 'Manual URL').
        'menu',            # Indicates which parent Menu container this item belongs to.
        'order',           # Display order to aid initial sorting or when not dragging.
    )
    
    # Makes the indented title clickable to go to the change form for the item.
    list_display_links = ('indented_title',)

    # Allows filtering menu items by their parent Menu container or link type.
    list_filter = ('menu', 'link_type',)
    
    # Fields that can be edited directly from the list view (for quick changes).
    list_editable = ('order', 'menu', 'link_type',)
    
    # MPTT-specific setting for the indentation width in the admin tree view.
    mptt_level_indent = 25 

    # Search functionality over translated title fields.
    search_fields = get_translated_fieldnames('title', model_kls=MenuItem)

    # Note: MenuItem model does not have a 'slug' field, so prepopulated_fields should not be set.
    # If a translable slug field existed on MenuItem, the implementation would be:
    # prepopulated_fields = get_translated_fieldnames('slug', model_kls=MenuItem)

    # Fields to display in the detailed change form for a single menu item.
    # This list should include all fields from the MenuItem model for editing.
    fields = (
        'menu',           # The parent Menu container.
        'parent',         # The parent MenuItem for nested hierarchy.
        'title',          # The translatable link text.
        'order',          # Display order.
        'link_type',      # Type of link (e.g., Page, Manual URL).
        'link_page',      # Conditional: linked Page object.
        'link_url',       # Conditional: manual URL string.
        'icon_class',     # Optional: FontAwesome icon class.
    )
