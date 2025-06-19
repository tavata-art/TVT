# File: menus/admin.py
from django.contrib import admin
from .models import Menu, MenuItem
from modeltranslation.admin import TabbedTranslationAdmin

# Usamos StackedInline que visualmente es mejor para campos con pestañas
class MenuItemInline(admin.StackedInline):
    model = MenuItem
    extra = 1
    ordering = ('order',)
    
    # ¡LA CLAVE! Definimos fieldsets DENTRO del inline
    fieldsets = (
        (None, {
            'fields': ('title', 'order'), # El título será renderizado con pestañas por modeltranslation
        }),
        ('Link (choose one)', {
            'classes': ('collapse',), # Hacemos esta sección colapsable
            'fields': ('link_page', 'link_url', 'icon_class'),
        }),
    )

@admin.register(Menu)
class MenuAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'slug')
    inlines = [MenuItemInline]

# También registramos MenuItem para poder editarlo por separado si queremos
@admin.register(MenuItem)
class MenuItemAdmin(TabbedTranslationAdmin):
     list_display = ('title', 'menu', 'order')