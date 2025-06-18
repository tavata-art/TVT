# File: widgets/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import WidgetZone, Widget
from modeltranslation.admin import TabbedTranslationAdmin


class WidgetInline(admin.TabularInline):
    """
    Defines the appearance of the widget editor when it's 'inlined'
    within the WidgetZone admin page. This allows for efficient management.
    """
    model = Widget
    # Fields to display for each widget row in the inline table
    fields = ('title', 'widget_type', 'order', 'item_count', 'cache_timeout', 'blog_category_filter', 'page_category_filter')
    extra = 1  # Provides one empty slot to add a new widget
    ordering = ['order']


@admin.register(WidgetZone)
class WidgetZoneAdmin(admin.ModelAdmin):
    """
    Admin options for the WidgetZone model.
    """
    list_display = ('name', 'slug', 'widget_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    # This embeds the inline widget editor directly into the zone's change page
    inlines = [WidgetInline]

    @admin.display(description=_("Number of Widgets"))
    def widget_count(self, obj):
        """Calculates and returns the number of widgets in this zone."""
        return obj.widgets.count()


# We also register the Widget model separately to have a global list view
@admin.register(Widget)
class WidgetAdmin(TabbedTranslationAdmin):
    """
    Admin options for the main Widget model list view.
    This provides a global overview of all widgets across all zones.
    """
    # Fields to display in the main list view for all widgets
    list_display = ('title', 'zone', 'widget_type', 'order', 'cache_timeout')
    
    # Filters available in the right sidebar
    list_filter = ('zone', 'widget_type')
    
    # Fields that can be edited directly from the list view
    list_editable = ('order', 'zone', 'cache_timeout')
    
    # Search functionality
    search_fields = ('title',)
    
    # Fields to display in the detailed change form for a single widget
    fields = ('title', 'zone', 'widget_type', 'order', 'item_count', 'cache_timeout', 'blog_category_filter', 'page_category_filter')

    # Default ordering
    ordering = ('zone', 'order')