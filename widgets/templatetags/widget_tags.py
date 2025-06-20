# File: widgets/templatetags/widget_tags.py
import logging
from django import template
from django.db.models import Count, Q
from django.core.cache import cache
from django.conf import settings

# Import all needed models at the top
from blog.models import Post
from categories.models import Category
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
        # 1. Create a unique, versioned, and language-specific cache key.
        language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
        cache_key = f'widget_items_{widget.id}_{language_code}_v1'
        
        # 2. Try to get the items from the cache first.
        items = None
        if widget.cache_timeout > 0:
            items = cache.get(cache_key)

        # 3. If it's a "cache miss" (items is None), query the database.
        if items is None:
            if widget.cache_timeout > 0:
                logger.info(f"CACHE MISS for widget '{widget.title}' (ID: {widget.id}). Querying database.")
            
            items_qs = Post.objects.none() # Default empty queryset

            # --- WIDGET LOGIC DISPATCHER (match/case) ---
            match widget.widget_type:
                case 'recent_posts' | 'most_viewed_posts' | 'most_commented_posts' | 'editor_picks_posts':
                    # This block handles all post-based widgets
                    if widget.widget_type == 'recent_posts':
                        items_qs = Post.objects.filter(status='published').order_by('-published_date')
                    elif widget.widget_type == 'most_viewed_posts':
                        items_qs = Post.objects.filter(status='published').order_by('-views_count', '-published_date')
                    elif widget.widget_type == 'most_commented_posts':
                        items_qs = Post.objects.filter(status='published') \
                                               .annotate(num_comments=Count('comments', filter=Q(comments__is_approved=True))) \
                                               .filter(num_comments__gt=0) \
                                               .order_by('-num_comments', '-published_date')
                    elif widget.widget_type == 'editor_picks_posts':
                        items_qs = Post.objects.filter(status='published', editor_rating__gt=0) \
                                               .order_by('-editor_rating', '-published_date')
                    
                    # Apply slicing and evaluate the queryset
                    items = list(items_qs[:widget.item_count])

                case 'blog_categories':
                    # This case handles the blog category widget specifically
                    items = list(
                        Category.objects.annotate(
                            num_blog_posts=Count('blog_posts', filter=Q(blog_posts__status='published'))
                        ).filter(num_blog_posts__gt=0).order_by('-num_blog_posts', 'name')[:widget.item_count]
                    )
                
                case _:
                    logger.warning(f"Unrecognized widget type '{widget.widget_type}' for widget '{widget.title}'.")
                    items = [] # Default to an empty list
            
            # 4. Store the result in the cache if a timeout is set.
            if widget.cache_timeout > 0:
                cache.set(cache_key, items, widget.cache_timeout)
        else:
            logger.info(f"CACHE HIT for widget '{widget.title}' (ID: {widget.id}). Serving from cache.")

        # --- END CACHING LOGIC ---
        
        widget_data = {'widget': widget, 'items': items}
        processed_widgets.append(widget_data)
        
    return {'processed_widgets': processed_widgets, 'request': context['request']}