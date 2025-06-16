# blog/templatetags/blog_tags.py
from django import template
from ..models import Post, PostCategory

register = template.Library()

@register.inclusion_tag('blog/partials/_recent_posts_widget.html')
def show_recent_posts(count=5):
    """
    Displays a list of the most recent published posts.
    """
    recent_posts = Post.objects.filter(status='published').order_by('-published_date')[:count]
    return {'recent_posts': recent_posts}

@register.inclusion_tag('blog/partials/_blog_categories_widget.html')
def show_blog_categories():
    """
    Displays a list of all blog categories.
    """
    categories = PostCategory.objects.all()
    return {'categories': categories}