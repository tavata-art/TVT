# pages/admin.py
from django.contrib import admin
from .models import Page, Category
from django_summernote.admin import SummernoteModelAdmin

# --- REGISTRO DEL NUEVO MODELO CATEGORY ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

# --- PAGEADMIN MODIFICADO ---
@admin.register(Page)
class PageAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)

    list_display = ('title', 'author', 'status', 'display_categories', 'created_at')
    list_filter = ('status', 'author', 'categories') # ¡Añadimos filtro por categoría!
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('status', '-created_at')

    # ¡NUEVO CAMPO! Usamos filter_horizontal para una mejor interfaz
    # en lugar de una lista de selección múltiple simple.
    filter_horizontal = ('categories',)

    # Método para mostrar las categorías en la lista de páginas
    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categorías'

