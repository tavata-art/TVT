# blog/admin.py
from django.contrib import admin
from .models import Post, PostCategory
from django_summernote.admin import SummernoteModelAdmin

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('title', 'author', 'status', 'published_date')
    list_filter = ('status', 'created_at', 'published_date', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ('status', '-published_date')

# Register your models here.
