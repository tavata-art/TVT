from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Post, PostCategory
from django_summernote.admin import SummernoteModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin

@admin.register(PostCategory)
class PostCategoryAdmin(TabbedTranslationAdmin):
    """ Admin options for the PostCategory model. """
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    """ Admin options for the Post model, integrating Summernote and ModelTranslation. """
    
    list_display = ('title', 'author', 'status', 'published_date')
    list_filter = ('status', 'published_date', 'author', 'categories')
    search_fields = ('title', 'content')
    date_hierarchy = 'published_date'
    ordering = ('status', '-published_date')
    
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories',)
    summernote_fields = ('content',)