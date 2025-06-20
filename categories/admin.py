# File: categories/admin.py
from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Category

@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin, DraggableMPTTAdmin):
    """
    Admin options for the universal Category model.
    
    This admin class combines the power of two libraries:
    - `TabbedTranslationAdmin`: Provides tabs for multilingual fields (name, slug, etc.).
    - `DraggableMPTTAdmin`: Provides an intuitive, drag-and-drop interface for
      managing the category hierarchy.
    """
    
    # --- Configuration for MPTT ---
    # `DraggableMPTTAdmin` automatically creates a tree view.
    # We specify the columns to display in that tree view.
    list_display = (
        'tree_actions',    # Provides the drag handle and action buttons
        'indented_title',  # The special field from MPTT that shows the name with indentation
        'slug',            # The non-translated slug for reference
    )
    
    # This makes the main title clickable to go to the change form
    list_display_links = ('indented_title',)
    
    # MPTT-specific setting for the indentation width
    mptt_level_indent = 20

    # --- Configuration for ModelTranslation ---
    # `prepopulated_fields` must be specified for each language
    prepopulated_fields = {
        'slug_en': ('name_en',),
        'slug_es': ('name_es',),
        'slug_ca': ('name_ca',)
    }
    
    # --- Standard Django Admin Configuration ---
    search_fields = ('name_en', 'name_es', 'name_ca')