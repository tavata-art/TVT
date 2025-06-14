# pages/admin.py
from django.contrib import admin
from .models import Page
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Page)
class PageAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    """
    Configuración personalizada para el modelo Page en el admin.
    """
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'author')
    search_fields = ('title', 'content')
    
    # ¡Magia! Esto autocompleta el campo slug a partir del título mientras escribes.
    prepopulated_fields = {'slug': ('title',)} 
    
    date_hierarchy = 'created_at'
    ordering = ('status', '-created_at')
