# widgets/templatetags/widget_tags.py
import logging
from django import template
from django.db.models import Count, Q

# Importa los modelos que necesitarás para las consultas
from blog.models import Post, PostCategory
from pages.models import Page, Category as PageCategory
from widgets.models import WidgetZone


logger = logging.getLogger(__name__)
register = template.Library()

@register.inclusion_tag('widgets/render_zone.html', takes_context=True)
def show_widget_zone(context, zone_slug):
    """
    Renders all widgets assigned to a specific WidgetZone using a match/case dispatcher.
    """
    try:
        zone = WidgetZone.objects.prefetch_related('widgets').get(slug=zone_slug)
        widgets = zone.widgets.all()
    except WidgetZone.DoesNotExist:
        logger.warning(f"Widget zone with slug '{zone_slug}' not found.")
        return {'processed_widgets': []} # Return early if zone doesn't exist

    processed_widgets = []
    for widget in widgets:
        # Initialize with a default empty queryset
        items_qs = Post.objects.none() 

        # --- WIDGET LOGIC DISPATCHER using match/case ---
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
                # This case returns a different model, so we handle it separately
                category_qs = PostCategory.objects.annotate(
                                    num_posts=Count('posts', filter=Q(posts__status='published'))
                                ).filter(num_posts__gt=0).order_by('-num_posts', 'name')
                
                # We limit the categories here if item_count should apply
                widget_data = {'widget': widget, 'items': category_qs[:widget.item_count]}
                processed_widgets.append(widget_data)
                logger.debug(f"Widget '{widget.title}': Found {category_qs.count()} categories.")
                continue  # Skip the common logic below for this special case

            case _: # Default case for unrecognized widget types
                logger.warning(f"Widget type '{widget.widget_type}' for widget '{widget.title}' has no defined logic.")
                # items_qs remains an empty queryset
        
        # Common logic for all Post-based widgets (slicing)
        final_items = items_qs[:widget.item_count]
        
        widget_data = {'widget': widget, 'items': final_items}
        processed_widgets.append(widget_data)
        logger.debug(f"Widget '{widget.title}': Found {final_items.count()} items.")
        
    return {'processed_widgets': processed_widgets, 'request': context['request']}