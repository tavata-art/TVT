# File: categories/admin.py
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Category

@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin, MPTTModelAdmin):
    """
    Admin options for the universal, hierarchical Category model.
    It uses MPTT for tree display and ModelTranslation for multilingual fields.
    """
    # MPTTModelAdmin will handle the display to show the tree structure.
    # We can add list_display if we want to customize columns, but the default is good.
    list_display = ('name',) # A simple display

    # Configure prepopulated fields for each language
    prepopulated_fields = {'slug_en': ('name_en',), 'slug_es': ('name_es',), 'slug_ca': ('name_ca',)}

    # MPTT indent configuration
    mptt_level_indent = 20
