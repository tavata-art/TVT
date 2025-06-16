from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Page, Category
from django_summernote.admin import SummernoteModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin

@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    """ Admin options for the Category model. """
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Page)
class PageAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    """ Admin options for the Page model, integrating Summernote and ModelTranslation. """
    
    # What fields to display in the list view
    list_display = ('title', 'author', 'status', 'is_homepage', 'display_categories')
    
    # Filters in the right sidebar
    list_filter = ('status', 'author', 'categories', 'is_homepage')
    
    # Search functionality
    search_fields = ('title', 'content')
    
    # Ordering
    ordering = ('-created_at',)
    
    # Auto-populate the slug field from the title
    prepopulated_fields = {'slug': ('title',)}
    
    # A nicer widget for ManyToMany fields
    filter_horizontal = ('categories',)
    
    # Tell Summernote which field(s) to use its WYSIWYG editor on
    summernote_fields = ('content',)

    def display_categories(self, obj):
        """ Creates a string for the Categories column. """
        return ", ".join([category.name for category in obj.categories.all()])
    
    # Set the column header for our custom method
    display_categories.short_description = _("Categories")