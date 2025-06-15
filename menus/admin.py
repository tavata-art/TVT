# menus/admin.py
from django.contrib import admin
from .models import MenuItem
from modeltranslation.admin import TabbedTranslationAdmin

@admin.register(MenuItem)
class MenuItemAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'order', 'link_page', 'link_url')
    list_editable = ('order',)
    search_fields = ('title',)
    list_filter = ('link_page',)
