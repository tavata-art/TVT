# File: categories/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import Category

@receiver([post_save, post_delete], sender=Category)
def clear_category_tree_cache(sender, instance, **kwargs):
    """
    Clears the cached category tree for all languages whenever a category
    is saved or deleted.
    """
    print("--- CATEGORY SIGNAL TRIGGERED: Clearing all category tree caches ---")
    for lang_code, _ in settings.LANGUAGES:
        cache_key = f'full_category_tree_nodes_{lang_code}_v1'
        cache.delete(cache_key)