# blog/templatetags/blog_tags.py
from django import template
from ..models import Post, PostCategory
from site_settings.models import SiteConfiguration

register = template.Library()

@register.inclusion_tag('blog/partials/_recent_posts_widget.html')
def show_recent_posts(): # Eliminamos el argumento 'count'
    site_config = SiteConfiguration.objects.get()
    count = site_config.recent_posts_widget_count # Leemos el valor
    recent_posts = Post.objects.filter(status='published').order_by('-published_date')[:count]
    return {'recent_posts': recent_posts}

@register.inclusion_tag('blog/partials/_blog_categories_widget.html')
def show_blog_categories():
    """
    Displays a list of all blog categories.
    """
    categories = PostCategory.objects.all()
    return {'categories': categories}