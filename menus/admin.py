# menus/admin.py
from django.contrib import admin
from .models import Menu, MenuItem
from modeltranslation.admin import TabbedTranslationAdmin # Importamos para la internacionalización

# Esta clase define cómo se verán los MenuItem DENTRO de la página de un Menu
class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1 # Muestra un campo vacío para añadir un nuevo item
    ordering = ['order']

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [MenuItemInline] # ¡Aquí adjuntamos el inline!

# También es bueno tener acceso a los MenuItem por separado, aunque no es estrictamente necesario
@admin.register(MenuItem)
class MenuItemAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'menu', 'order')
    list_filter = ('menu',)
    list_editable = ('order',)
