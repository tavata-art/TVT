# widgets/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from blog.models import Post # Importamos Post porque sus cambios afectan a los widgets
from .models import Widget

def clear_all_widget_caches():
    """
    A simple but effective strategy: clear ALL widget caches.
    A more granular approach is possible but much more complex.
    """
    # Obtenemos TODOS los widgets de la base de datos
    all_widgets = Widget.objects.all()
    # Para cada widget y cada idioma, construimos la clave y la borramos
    for widget in all_widgets:
        for lang_code, _ in settings.LANGUAGES:
            cache_key = f'widget_items_{widget.id}_{lang_code}_v1'
            cache.delete(cache_key)
    print("--- ALL WIDGET CACHES CLEARED ---")


# Si se guarda o borra un Widget
@receiver([post_save, post_delete], sender=Widget)
def on_widget_change(sender, instance, **kwargs):
    clear_all_widget_caches()

# ¡LA PARTE IMPORTANTE!
# Si se guarda o borra un Post, los widgets de "Recientes", "Vistos", etc.,
# deben actualizarse.
@receiver([post_save, post_delete], sender=Post)
def on_post_change(sender, instance, **kwargs):
    clear_all_widget_caches()

# En el futuro, podríamos añadir signals para Comments, Pages, etc.