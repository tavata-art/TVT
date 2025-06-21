# File: widgets/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import WidgetZone, Widget
from modeltranslation.admin import TabbedTranslationAdmin

class WidgetInline(admin.TabularInline):
    """
    Defines the editor for Widgets when they are managed 'inline'
    within a WidgetZone.
    """
    model = Widget
    # We now use the single, universal 'category_filter' field.
    fields = ('title', 'widget_type', 'order', 'item_count', 'cache_timeout', 'category_filter', 'column_count', 'section_title', 'view_all_link_text', 'view_all_link_url')
    extra = 1
    ordering = ['order']
    # Adding a class to make the inline editor more compact
    classes = ('collapse',)


@admin.register(WidgetZone)
class WidgetZoneAdmin(admin.ModelAdmin):
    """ Admin options for the WidgetZone model. """
    list_display = ('name', 'slug', 'widget_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [WidgetInline]

    @admin.display(description=_("Number of Widgets"))
    def widget_count(self, obj):
        """Calculates the number of widgets in this zone."""
        return obj.widgets.count()


@admin.register(Widget)
class WidgetAdmin(TabbedTranslationAdmin):
    """ 
    A global list view for all Widgets, allowing for quick edits and
    re-assignment across different zones.
    """
    list_display = ('title', 'zone', 'widget_type', 'order', 'cache_timeout')
    list_filter = ('zone', 'widget_type')
    list_editable = ('order', 'zone', 'cache_timeout')
    search_fields = ('title',)
    
    # We update the fields for the detail edit form as well.
    fields = ('title', 'zone', 'widget_type', 'order', 'item_count', 'cache_timeout', 'category_filter')

    ordering = ('zone', 'order')
