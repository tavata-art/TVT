from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Menu, MenuItem
from modeltranslation.admin import TabbedTranslationAdmin

class MenuItemInline(admin.TabularInline):
    """
    Allows editing MenuItems directly within the Menu admin page.
    This is a more user-friendly approach.
    """
    model = MenuItem
    extra = 1 # Shows one empty slot for a new item
    ordering = ['order']
    # If the inline form gets too wide, you can specify fields to show:
    # fields = ('title', 'order', 'link_page', 'link_url', 'icon_class')


@admin.register(Menu)
class MenuAdmin(TabbedTranslationAdmin): # Making Menu title translatable
    """ Admin options for the Menu model. """
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [MenuItemInline] # This embeds the MenuItem editor


@admin.register(MenuItem)
class MenuItemAdmin(TabbedTranslationAdmin):
    """
    Provides a separate admin view for all MenuItems,
    which is useful for managing all links at once.
    """
    list_display = ('title', 'menu', 'order', 'link_page', 'link_url')
    list_filter = ('menu',)
    list_editable = ('order',)
    search_fields = ('title', 'link_url')