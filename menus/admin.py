from django.contrib import admin
from django.conf import settings
from mptt.admin import DraggableMPTTAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Menu, MenuItem

def get_translated_fieldnames(field_base):
    """
    Returns a tuple of field names for all languages defined in settings.LANGUAGES.
    Example: ('title_en', 'title_es', 'title_ca', ...)
    """
    return tuple(f"{field_base}_{lang[0]}" for lang in settings.LANGUAGES)

@admin.register(Menu)
class MenuAdmin(TabbedTranslationAdmin):
    """
    Admin for the main Menu containers.
    It's kept simple, as the real management happens in MenuItemAdmin.
    """
    list_display = ('title', 'slug')
    search_fields = get_translated_fieldnames('title')
    prepopulated_fields = {'slug': (get_translated_fieldnames('title')[0],)}

@admin.register(MenuItem)
class MenuItemAdmin(DraggableMPTTAdmin, TabbedTranslationAdmin):
    """
    Admin for the hierarchical MenuItem model.
    This provides a draggable, nested interface for easy menu management.
    """
    list_display = (
        'tree_actions',
        'indented_title',
        'link_type',
    )
    list_display_links = ('indented_title',)
    list_filter = ('menu',)
    mptt_level_indent = 25