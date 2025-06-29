# File: tags/admin.py

from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Tag

@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    list_display = ('__str__', 'slug')
    search_fields = ['translations__label']
