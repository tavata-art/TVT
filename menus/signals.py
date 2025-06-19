# File: menus/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import MenuItem, Menu

@receiver([post_save, post_delete], sender=MenuItem)
def clear_menu_cache(sender, instance, **kwargs):
    """
    Clears the relevant menu cache whenever a MenuItem is saved or deleted.
    """
    # We need to clear the cache for all languages
    from django.conf import settings
    if instance.menu:
        for lang_code, lang_name in settings.LANGUAGES:
            cache_key = f'menu_items_{instance.menu.slug}_{lang_code}_v1'
            cache.delete(cache_key)
        print(f"Cache cleared for menu '{instance.menu.slug}'")