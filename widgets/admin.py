# widgets/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import WidgetZone, Widget
from modeltranslation.admin import TabbedTranslationAdmin

# Esta clase define cómo se verá cada fila de Widget DENTRO de la página de WidgetZone
class WidgetInline(admin.TabularInline):
    model = Widget
    # Los campos que se mostrarán en la tabla inline
    fields = ('title', 'widget_type', 'order', 'item_count', 'blog_category_filter')
    extra = 1  # Muestra una fila vacía para añadir un nuevo widget
    ordering = ['order']

@admin.register(WidgetZone)
class WidgetZoneAdmin(admin.ModelAdmin):
    """
    Admin for Widget Zones. Allows managing widgets directly within each zone.
    """
    list_display = ('name', 'slug', 'widget_count')
    prepopulated_fields = {'slug': ('name',)}
    # Adjuntamos el editor de Widgets inline
    inlines = [WidgetInline]

    def widget_count(self, obj):
        return obj.widgets.count()
    widget_count.short_description = _("Number of Widgets")

# También registramos el modelo Widget por separado para tener una vista global
@admin.register(Widget)
class WidgetAdmin(TabbedTranslationAdmin):
    """
    A global view for all widgets, allowing filtering by zone or type.
    """
    list_display = ('title', 'zone', 'widget_type', 'order')
    list_filter = ('zone', 'widget_type')
    list_editable = ('order', 'zone') # Permite cambiar el orden y la zona rápidamente
    fields = ('title', 'zone', 'widget_type', 'order', 'item_count', 'blog_category_filter', 'page_category_filter')