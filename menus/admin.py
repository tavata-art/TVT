# File: menus/admin.py
from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Menu, MenuItem

@admin.register(Menu)
class MenuAdmin(TabbedTranslationAdmin):
    """
    Admin for the main Menu containers.
    It's kept simple, as the real management happens in MenuItemAdmin.
    """
    list_display = ('title', 'slug')
    search_fields = ('title_en', 'title_es', 'title_ca')
    prepopulated_fields = {'slug': ('title_en',)}


@admin.register(MenuItem)
class MenuItemAdmin(DraggableMPTTAdmin, TabbedTranslationAdmin):
    """
    Admin for the hierarchical MenuItem model.
    This provides a draggable, nested interface for easy menu management.
    """
    # The fields to display in the tree view list
    list_display = (
        'tree_actions',    # The drag handle and actions
        'indented_title',  # The item's title, indented correctly
        'link_type',
    )

    # Make the main title clickable
    list_display_links = ('indented_title',)

    # Allow filtering by the parent menu
    list_filter = ('menu',)

    # MPTT-specific setting for the indentation width
    mptt_level_indent = 25