# File: widgets/templatetags/widget_tags.py
import logging
from django import template
from django.db.models import Count, Q
from django.core.cache import cache
from django.conf import settings # Needed for settings.LANGUAGES and settings.LANGUAGE_CODE

# Import all needed models at the top
from blog.models import Post 
from categories.models import Category # Universal Category model
from widgets.models import Widget, WidgetZone

# Ensure static is imported from Django's template tags
from django.templatetags.static import static 

logger = logging.getLogger(__name__)
register = template.Library()

# --- HELPER FUNCTION: GET THUMBNAIL URL ---
def _get_thumbnail_url(obj):
    """
    Returns the URL for the thumbnail of a given object.
    Currently supports Post objects with 'featured_image'.
    """
    if isinstance(obj, Post) and obj.featured_image:
        return obj.featured_image.url
    
    # Fallback to a default placeholder image if no specific image is found.
    # You MUST ensure 'static/images/placeholders/default_thumbnail.png' exists.
    return static('images/placeholders/default_thumbnail.png')

@register.inclusion_tag('widgets/render_zone.html', takes_context=True)
def show_widget_zone(context, zone_slug):
    """
    Renders all widgets for a specific zone, utilizing a configurable cache
    for each widget to optimize performance.
    """
    try:
        zone = WidgetZone.objects.prefetch_related('widgets').get(slug=zone_slug)
        widgets_queryset = zone.widgets.all()
    except WidgetZone.DoesNotExist:
        logger.warning(f"Widget zone with slug '{zone_slug}' not found.")
        return {'processed_widgets': []} # Return empty if zone doesn't exist

    processed_widgets = [] # Initialize this list here, outside the loop

    # Iterate through each widget configured for this zone
    for widget_instance in widgets_queryset: # Renamed to widget_instance for clarity
        language_code = context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE)
        cache_key = f'widget_items_{widget_instance.id}_{language_code}_v1'
        
        items_to_cache = None # Initialize variable that will hold items for caching
        
        # 1. Try to get items from cache if caching is enabled for this widget.
        if widget_instance.cache_timeout > 0:
            items_to_cache = cache.get(cache_key)

        # 2. If it's a cache miss, query the database and process.
        if items_to_cache is None:
            if widget_instance.cache_timeout > 0: # Log only if caching was attempted
                logger.info(f"CACHE MISS for widget '{widget_instance.title}' (ID: {widget_instance.id}). Querying database.")
            
            # --- WIDGET LOGIC DISPATCHER (match/case) ---
            # This 'items_container' will hold the list of items from the DB query.
            items_container = [] # Initialize for the match/case block

            match widget_instance.widget_type:
                case 'recent_posts':
                    items_qs = Post.objects.filter(status='published').order_by('-published_date')
                    items_container = list(items_qs[:widget_instance.item_count]) # Evaluate QuerySet
                
                case 'most_viewed_posts':
                    items_qs = Post.objects.filter(status='published').order_by('-views_count', '-published_date')
                    items_container = list(items_qs[:widget_instance.item_count])

                case 'most_commented_posts':
                    items_qs = Post.objects.filter(status='published') \
                                           .annotate(num_comments=Count('comments', filter=Q(comments__is_approved=True))) \
                                           .filter(num_comments__gt=0) \
                                           .order_by('-num_comments', '-published_date')
                    items_container = list(items_qs[:widget_instance.item_count])
                
                case 'editor_picks_posts':
                    items_qs = Post.objects.filter(status='published', editor_rating__gt=0) \
                                           .order_by('-editor_rating', '-published_date')
                    items_container = list(items_qs[:widget_instance.item_count])
                
                case 'blog_categories':
                    categories_qs = Category.objects.annotate(
                        num_blog_posts=Count('blog_posts', filter=Q(blog_posts__status='published'))
                    ).filter(num_blog_posts__gt=0).order_by('-num_blog_posts', 'name')
                    items_container = list(categories_qs[:widget_instance.item_count])
                
                # --- NEW CASES FOR POST GRIDS ---
                case 'post_grid_recent':
                    items_qs = Post.objects.filter(status='published').order_by('-published_date')
                    items_container = list(items_qs[:widget_instance.item_count])
                    # No new thumbnail_url required here, as the template will handle it dynamically.

                case 'post_grid_popular':
                    items_qs = Post.objects.filter(status='published').order_by('-views_count', '-published_date')
                    items_container = list(items_qs[:widget_instance.item_count])

                case 'post_grid_commented':
                    items_qs = Post.objects.filter(status='published') \
                                           .annotate(num_comments=Count('comments', filter=Q(comments__is_approved=True))) \
                                           .filter(num_comments__gt=0) \
                                           .order_by('-num_comments', '-published_date')
                    items_container = list(items_qs[:widget_instance.item_count])
                
                case 'post_grid_editor':
                    items_qs = Post.objects.filter(status='published', editor_rating__gt=0) \
                                           .order_by('-editor_rating', '-published_date')
                    items_container = list(items_qs[:widget_instance.item_count])


                case _: # Unrecognized widget type
                    logger.warning(f"Unrecognized widget type '{widget_instance.widget_type}' for widget '{widget_instance.title}'.")
                    items_container = [] # Empty list for safety.
            
            # --- Common Post-based Processing (Applies only to Post items) ---
            # Attach thumbnail_url to Post objects. This runs once per item on cache miss.
            # This should not run for categories.
            if widget_instance.widget_type in ['recent_posts', 'most_viewed_posts', 'most_commented_posts', 'editor_picks_posts', 'post_grid_recent', 'post_grid_popular', 'post_grid_commented', 'post_grid_editor']:
                for post_obj in items_container: 
                    # post_obj is already a Post instance here (from items_container)
                    post_obj.thumbnail_url = _get_thumbnail_url(post_obj)
            
            items_to_cache = items_container # Assign the processed list for caching

            # 3. Store result in cache if timeout is set.
            if widget_instance.cache_timeout > 0: # Only cache if timeout > 0
                cache.set(cache_key, items_to_cache, widget_instance.cache_timeout)
                logger.info(f"CACHE SET for widget '{widget_instance.title}' (ID: {widget_instance.id}) for {widget_instance.cache_timeout} seconds.")
        else: # Cache HIT
            logger.info(f"CACHE HIT for widget '{widget_instance.title}' (ID: {widget_instance.id}). Serving from cache.")

        # --- IMPORTANT: Append to processed_widgets list outside the `if items_to_cache is None` block ---
        # `items_to_cache` will hold either the cached value or the newly fetched value.
        processed_widgets.append({'widget': widget_instance, 'items': items_to_cache})
        
    return {'processed_widgets': processed_widgets, 'request': context['request']}