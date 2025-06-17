# widgets/templatetags/widget_tags.py
from django import template
from django.db.models import Count, Q

# Importa los modelos que necesitarás para las consultas
from blog.models import Post, PostCategory
from pages.models import Page, Category as PageCategory
from widgets.models import WidgetZone

register = template.Library()

@register.inclusion_tag('widgets/render_zone.html', takes_context=True)
def show_widget_zone(context, zone_slug):
    """
    Renders all widgets assigned to a specific WidgetZone.
    Each widget type can have its own template and logic.
    """
    try:
        # prefetch_related is a performance optimization
        zone = WidgetZone.objects.prefetch_related('widgets').get(slug=zone_slug)
        widgets = zone.widgets.all()
    except WidgetZone.DoesNotExist:
        widgets = []

    # We process the data for each widget before sending to the template
    processed_widgets = []
    for widget in widgets:
        widget_data = {
            'widget': widget,
            'items': None, # Default to None
        }

        # --- WIDGET LOGIC DISPATCHER ---
        # Based on the widget type, we perform a specific query

        if widget.widget_type == 'recent_posts':
            widget_data['items'] = Post.objects.filter(status='published').order_by('-published_date')[:widget.item_count]

        elif widget.widget_type == 'most_viewed_posts':
            widget_data['items'] = Post.objects.filter(status='published').order_by('-views_count', '-published_date')[:widget.item_count]

        elif widget.widget_type == 'most_commented_posts':
            widget_data['items'] = Post.objects.filter(status='published') \
                                               .annotate(num_comments=Count('comments', filter=Q(comments__is_approved=True))) \
                                               .filter(num_comments__gt=0) \
                                               .order_by('-num_comments', '-published_date')[:widget.item_count]

        elif widget.widget_type == 'blog_categories':
            widget_data['items'] = PostCategory.objects.annotate(
                                        num_posts=Count('posts', filter=Q(posts__status='published'))
                                    ).filter(num_posts__gt=0).order_by('-num_posts', 'name')[:widget.item_count]

        # Add more elif blocks here for future widget types...

        processed_widgets.append(widget_data)

    # Pass the request object from the main context into our tag's context
    return {'processed_widgets': processed_widgets, 'request': context['request']}