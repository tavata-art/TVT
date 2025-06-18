# File: widgets/templatetags/widget_tags.py
import logging
from django import template
from django.db.models import Count, Q
from django.core.cache import cache

from blog.models import Post, PostCategory
from widgets.models import Widget, WidgetZone 

logger = logging.getLogger(__name__)
register = template.Library()

@register.inclusion_tag('widgets/render_zone.html', takes_context=True)
def show_widget_zone(context, zone_slug):
    """
    Renders all widgets for a specific zone, utilizing a configurable cache
    for each widget to optimize performance.
    """
    try:
        zone = WidgetZone.objects.prefetch_related('widgets').get(slug=zone_slug)
        widgets = zone.widgets.all()
    except WidgetZone.DoesNotExist:
        logger.warning(f"Widget zone with slug '{zone_slug}' not found.")
        return {'processed_widgets': []}

    processed_widgets = []
    for widget in widgets:
        # 1. Create a unique cache key for this specific widget instance.
        cache_key = f'widget_items_{widget.id}_v1'
        
        # 2. Try to get the items from the cache first.
        #    If cache_timeout is 0, we bypass the cache get.
        items = None
        if widget.cache_timeout > 0:
            items = cache.get(cache_key)

        # 3. If it's a "cache miss" (items is None), we query the database.
        if items is None:
            # We only log the DB query if caching was attempted.
            if widget.cache_timeout > 0:
                logger.info(f"CACHE MISS for widget '{widget.title}' (ID: {widget.id}). Querying database.")
            
            items_qs = Post.objects.none()

            # --- WIDGET LOGIC DISPATCHER (match/case) ---
            match widget.widget_type:
                case 'recent_posts':
                    items_qs = Post.objects.filter(status='published').order_by('-published_date')
                
                case 'most_viewed_posts':
                    items_qs = Post.objects.filter(status='published').order_by('-views_count', '-published_date')

                case 'most_commented_posts':
                    items_qs = Post.objects.filter(status='published') \
                                           .annotate(num_comments=Count('comments', filter=Q(comments__is_approved=True))) \
                                           .filter(num_comments__gt=0) \
                                           .order_by('-num_comments', '-published_date')
                
                case 'editor_picks_posts':
                    items_qs = Post.objects.filter(status='published', editor_rating__gt=0) \
                                           .order_by('-editor_rating', '-published_date')
                
                case 'blog_categories':
                    category_qs = PostCategory.objects.annotate(
                                        num_posts=Count('posts', filter=Q(posts__status='published'))
                                    ).filter(num_posts__gt=0).order_by('-num_posts', 'name')
                    # We slice this queryset directly.
                    items = list(category_qs[:widget.item_count])

                case _:
                    logger.warning(f"Unrecognized widget type '{widget.widget_type}' for widget '{widget.title}'.")
                    items = []

            # If the widget type was post-based, we apply the slicing here.
            if widget.widget_type != 'blog_categories' and widget.widget_type in Widget.WidgetType.values:
                items = list(items_qs[:widget.item_count])

            # 4. Store the result in the cache if timeout is greater than 0.
            if widget.cache_timeout > 0:
                cache.set(cache_key, items, widget.cache_timeout)
        else:
            logger.info(f"CACHE HIT for widget '{widget.title}' (ID: {widget.id}). Serving from cache.")

        # --- END CACHING LOGIC ---
        
        widget_data = {'widget': widget, 'items': items}
        processed_widgets.append(widget_data)
        
    return {'processed_widgets': processed_widgets, 'request': context['request']}